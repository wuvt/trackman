from flask import current_app
from flask_restful import abort
from trackman import db, redis_conn, models, playlists_cache
from trackman.forms import AutomationTrackLogForm
from trackman.lib import log_track, find_or_add_track, logout_all_except, \
        is_automation_enabled
from trackman.view_utils import local_only
from .base import TrackmanStudioResource


class AutomationLog(TrackmanStudioResource):
    method_decorators = [local_only]

    def post(self):
        """
        Log a track played by automation
        ---
        operationId: logAutomationTrack
        tags:
        - trackman
        - tracklog
        - automation
        parameters:
        - in: form
          name: artist
          type: string
          required: true
          description: Artist name
        - in: form
          name: title
          type: string
          required: true
          description: Track title
        - in: form
          name: album
          type: string
          description: Album title
        - in: form
          name: label
          type: string
          description: Record label
        - in: form
          name: artist_mbid
          type: string
          description: Artist MBID
        - in: form
          name: recording_mbid
          type: string
          description: Recording MBID
        - in: form
          name: release_mbid
          type: string
          description: Release MBID
        - in: form
          name: releasegroup_mbid
          type: string
          description: Release Group MBID
        - in: form
          name: dj_id
          type: string
          description: DJ ID to use; will default to 1 if not provided
        responses:
          200:
            description: Track accepted, but not necessarily logged
            schema:
              type: object
              properties:
                success:
                  type: boolean
          201:
            description: Track logged
            schema:
              type: object
              properties:
                success:
                  type: boolean
          400:
            description: Bad request
          401:
            description: Invalid automation password
        """

        form = AutomationTrackLogForm(meta={'csrf': False})

        if form.password.data != current_app.config['AUTOMATION_PASSWORD']:
            abort(401, success=False, message="Invalid automation password")

        if not is_automation_enabled():
            return {
                'success': False,
                'error': "Automation not enabled",
            }

        title = form.title.data
        if len(title) <= 0:
            abort(400, success=False, message="Title must be provided")

        artist = form.artist.data
        if len(artist) <= 0:
            abort(400, success=False, message="Artist must be provided")

        album = form.album.data
        if len(album) <= 0:
            album = "Not Available"

        if artist.lower() in ("wuvt", "pro", "soo", "psa", "lnr", "ua"):
            # TODO: implement airlog logging
            return {
                'success': False,
                'message': "AirLog logging not yet implemented",
            }

        label = form.label.data

        new_track = models.Track(title, artist, album, label)
        new_track.artist_mbid = form.artist_mbid.data
        new_track.recording_mbid = form.recording_mbid.data
        new_track.release_mbid = form.release_mbid.data
        new_track.releasegroup_mbid = form.releasegroup_mbid.data

        # special handling if label is None
        if len(label) <= 0:
            label = "Not Available"

        track = find_or_add_track(new_track)

        dj_id_str = form.dj_id.data
        if len(dj_id_str) > 0:
            dj_id = int(dj_id_str)
        else:
            dj_id = 1

        # find a DJSet to use
        onair_dj_id = redis_conn.get('onair_dj_id')
        djset_id = redis_conn.get('onair_djset_id')

        if djset_id != None and onair_dj_id == dj_id:
            djset_id = int(djset_id)
        else:
            # find an existing automation DJSet to use or create a new one
            automation_set = logout_all_except(dj_id)
            if automation_set is not None:
                djset_id = automation_set.id
            else:
                automation_set = models.DJSet(dj_id)
                db.session.add(automation_set)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise
                playlists_cache.clear()

                djset_id = automation_set.id
                current_app.logger.info(
                    "Trackman: Automation DJSet ID {0} created for DJ ID "
                    "{1}".format(djset_id, dj_id))

            redis_conn.set('onair_dj_id', dj_id)
            redis_conn.set('onair_djset_id', djset_id)

        # check again if automation is enabled as the state may have changed
        # while we were running the above queries
        # if it is and we now have a valid DJSet, log the track
        if is_automation_enabled() and djset_id is not None:
            log_track(track.id, djset_id, track=track)
            return {'success': True}, 201
        else:
            return {'success': False}
