import datetime
from flask import current_app, request, session
from flask_restful import abort
from trackman import db, redis_conn, mail, models, signals
from trackman.lib import check_onair, disable_automation, \
    logout_all_except
from .base import TrackmanResource
from .schemas import AirLogSchema, TrackLogModifiedSchema


class DJSet(TrackmanResource):
    def get(self, djset_id):
        """
        Get information about a DJSet.
        ---
        operationId: getDjsetById
        tags:
        - private
        - djset
        parameters:
        - in: path
          name: djset_id
          type: integer
          required: true
          description: The ID of an existing DJSet
        responses:
          401:
            description: Session expired
          404:
            description: DJSet not found
        """
        djset = models.DJSet.query.get(djset_id)
        if not djset:
            abort(404, success=False, message="DJSet not found")

        if djset.dj_id != session.get('dj_id', None):
            abort(403, success=False)

        if djset.dtend is not None:
            abort(401, success=False, message="Session expired, please login again")

        if request.args.get('merged', False):
            airlog_schema = AirLogSchema()
            tracklog_schema = TrackLogModifiedSchema()

            logs = [tracklog_schema.dump(i) for i in djset.tracks]
            logs.extend([airlog_schema.dump(i) for i in djset.airlog])
            logs = sorted(logs, key=lambda log: log.get('airtime', False) if log.get('airtime', False) else log.get('played', False), reverse=False)

            return {
                'success': True,
                'logs': logs,
            }
        else:
            airlog_schema = AirLogSchema(many=True)
            tracklog_schema = TrackLogModifiedSchema(many=True)

            return {
                'success': True,
                'tracklog': tracklog_schema.dump(djset.tracks),
                'airlog': airlog_schema.dump(djset.airlog),
            }


class DJSetEnd(TrackmanResource):
    def post(self, djset_id):
        """
        End an existing DJSet.
        ---
        operation: endDjset
        tags:
        - private
        - djset
        responses:
          200:
            description: DJSet ended
        """
        djset = models.DJSet.query.with_for_update().get(djset_id)
        if not djset:
            abort(404, success=False, message="DJSet not found")

        if djset.dj_id != session.get('dj_id', None):
            abort(403, success=False)

        if djset.dtend is not None:
            abort(400, success=False, message="DJSet has already ended",
                  ended=True)

        djset.dtend = datetime.datetime.utcnow()

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        session.pop('dj_id', None)
        session.pop('djset_id', None)

        signals.dj_session_ended.send(self)

        if check_onair(djset_id):
            redis_conn.delete('onair_djset_id')

        # Reset the dj activity timeout period
        redis_conn.delete('dj_timeout')

        # Set dj_active expiration to NO_DJ_TIMEOUT to reduce automation
        # start time
        redis_conn.set('dj_active', 'false')
        redis_conn.expire(
            'dj_active', int(current_app.config['NO_DJ_TIMEOUT']))

        # email playlist
        if request.form.get('email_playlist', 'false') == 'true':
            tracks = models.TrackLog.query.\
                filter(models.TrackLog.djset_id == djset.id).\
                order_by(models.TrackLog.played).all()
            try:
                mail.send_playlist(djset, tracks)
            except Exception as exc:
                current_app.logger.warning(
                    "Trackman: Failed to send email for DJ set {0}: "
                    "{1}".format(djset.id, exc))

        return {
            'success': True,
        }


class DJSetList(TrackmanResource):
    def post(self):
        """
        Create a new DJSet.
        ---
        operation: createDjset
        tags:
        - private
        - djset
        responses:
          201:
            description: DJSet created
            schema:
              type: object
              properties:
                success:
                  type: boolean
                djset_id:
                  type: integer
                  description: The ID of the new DJSet
        """
        dj_id = session.get('dj_id', None)
        if dj_id is None:
            abort(403, success=False)

        dj = models.DJ.query.get(dj_id)
        if dj is None or dj.phone is None or dj.email is None:
            abort(403, success=False,
                  message="You must complete your DJ profile to continue.")

        disable_automation()

        # Close open DJSets, and see if we have one that belongs to the current
        # DJ that we can reuse
        djset = logout_all_except(dj.id)
        if djset is None:
            djset = models.DJSet(dj.id)
            db.session.add(djset)

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        signals.dj_session_started.send(self, djset=djset)

        redis_conn.set('onair_djset_id', djset.id)
        session['djset_id'] = djset.id

        return {
            'success': True,
            'djset_id': djset.id,
        }, 201
