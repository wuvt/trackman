import dateutil.parser
from flasgger import swag_from
from flask import session
from flask_restful import abort
from trackman import db, models, signals, ma
from trackman.forms import AirLogForm, AirLogEditForm
from .base import TrackmanOnAirResource


class AirLog(TrackmanOnAirResource):
    @swag_from({
        'operationId': "deleteAirLog",
        'tags': ['private', 'airlog'],
        'parameters': [
            {
                'in': "path",
                'name': "airlog_id",
                'type': "integer",
                'required': True,
                'description': "AirLog ID",
            },
        ],
        'responses': {
            200: {
                'description': "AirLog entry deleted",
            },
            404: {
                'description': "AirLog entry not found",
            },
        },
    })
    def delete(self, airlog_id):
        """Delete an existing AirLog entry."""
        airlog = models.AirLog.query.get(airlog_id)
        if not airlog:
            abort(404, success=False, message="AirLog entry not found")

        db.session.delete(airlog)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        signals.airlog_deleted.send(self, airlog)
        return {'success': True}

    @swag_from({
        'operationId': "modifyAirLog",
        'tags': ['private', 'airlog'],
        'parameters': [
            {
                'in': "path",
                'name': "airlog_id",
                'type': "integer",
                'required': True,
                'description': "AirLog ID",
            },
            {
                'in': "form",
                'name': "airtime",
                'type': "string",
                'description': "Air time",
            },
            {
                'in': "form",
                'name': "logtype",
                'type': "integer",
                'description': "Log type",
            },
            {
                'in': "form",
                'name': "logid",
                'type': "integer",
                'description': "Log ID",
            },
        ],
        'responses': {
            200: {
                'description': "AirLog entry modified",
            },
            400: {
                'description': "Bad request",
            },
            404: {
                'description': "AirLog entry not found",
            },
        },
    })
    def post(self, airlog_id):
        """Modify an existing logged AirLog entry."""
        airlog = models.AirLog.query.get(airlog_id)
        if not airlog:
            abort(404, success=False, message="AirLog entry not found")

        form = AirLogEditForm(meta={'csrf': False})

        # Update aired time
        airtime = form.airtime.data
        if len(airtime) > 0:
            airlog.airtime = dateutil.parser.parse(airtime)

        logtype = form.logtype.data
        if logtype > 0:
            airlog.logtype = logtype

        logid = form.logid.data
        if logid > 0:
            airlog.logid = logid

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        signals.airlog_modified.send(self, airlog)
        return {'success': True}


class AirLogCreateResponseSchema(ma.Schema):
    success = ma.Boolean()
    airlog_id = ma.Integer()


class AirLogList(TrackmanOnAirResource):
    @swag_from({
        'operationId': "createAirLog",
        'tags': ['private', 'airlog'],
        'parameters': [
            {
                'in': "form",
                'name': "djset_id",
                'type': "integer",
                'required': True,
                'description': "The ID of an existing DJSet",
            },
            {
                'in': "form",
                'name': "airtime",
                'type': "string",
                'description': "Air time",
            },
            {
                'in': "form",
                'name': "logtype",
                'type': "integer",
                'description': "Log type",
            },
            {
                'in': "form",
                'name': "logid",
                'type': "integer",
                'description': "Log ID",
            },
        ],
        'responses': {
            201: {
                'description': "AirLog entry created",
            },
            400: {
                'description': "Bad request",
            },
        },
    })
    def post(self):
        """Create a new AirLog entry."""
        form = AirLogForm(meta={'csrf': False})

        djset_id = form.djset_id.data
        if djset_id != session['djset_id']:
            abort(403, success=False)

        airlog = models.AirLog(djset_id, form.logtype.data, form.logid.data)
        db.session.add(airlog)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        signals.airlog_added.send(self, airlog=airlog)

        schema = AirLogCreateResponseSchema()
        return schema.dump({
            'success': True,
            'airlog_id': airlog.id,
        }), 201
