import datetime
from flask import request
from flask_restful import abort, Resource
from trackman import db
from trackman.lib import get_current_tracklog
from trackman.models import DJ, DJSet, Track, TrackLog
from trackman.view_utils import list_archives
from .base import PlaylistResource
from .schemas import DJSchema, DJSetSchema, TrackSchema, TrackLogSchema, \
        TrackLogLegacySchema


class NowPlaying(PlaylistResource):
    def get(self):
        """
        Retrieve information about what is currently playing.
        ---
        operationId: getNowPlaying
        tags:
        - trackman
        - playlists
        - tracklog
        - track
        """
        tracklog = get_current_tracklog()
        tracklog_schema = TrackLogSchema()
        return tracklog_schema.dump(tracklog)


class Last15Tracks(PlaylistResource):
    def get(self):
        """
        Retrieve information about the last 15 tracks that were played.
        ---
        operationId: getLast15
        tags:
        - trackman
        - playlists
        - tracklog
        - track
        """
        tracks = TrackLog.query.order_by(db.desc(TrackLog.id)).limit(15).all()
        tracklogs_schema = TrackLogSchema(many=True)
        return {
            'tracks': tracklogs_schema.dump(tracks),
        }


class LatestTrack(PlaylistResource):
    def get(self):
        """
        Retrieve information about what is currently playing in the old format.
        ---
        operationId: getLatestTrack
        tags:
        - trackman
        - playlists
        - tracklog
        - track
        """
        tracklog = get_current_tracklog()
        tracklog_schema = TrackLogLegacySchema()
        return tracklog_schema.dump(tracklog)


class PlaylistsByDay(PlaylistResource):
    def get(self, year, month, day):
        """
        Get a list of playlists played on a particular day.
        ---
        operationId: getPlaylistsByDay
        tags:
        - trackman
        - track
        parameters:
        - in: path
          name: year
          type: integer
          required: true
          description: Year
        - in: path
          name: month
          type: integer
          required: true
          description: Month
        - in: path
          name: day
          type: integer
          required: true
          description: Day of month
        responses:
          404:
            description: No playlists found
        """
        dtstart = datetime.datetime(year, month, day, 0, 0, 0)
        dtend = datetime.datetime(year, month, day, 23, 59, 59)
        sets = DJSet.query.\
            filter(DJSet.dtstart >= dtstart, DJSet.dtstart <= dtend).\
            all()
        djsets_schema = DJSetSchema(many=True)

        status_code = 200
        if len(sets) <= 0:
            # return 404 if no playlists found
            status_code = 404

        return {
            'dtstart': dtstart,
            'sets': djsets_schema.dump(sets),
        }, status_code


class PlaylistsByDateRange(Resource):
    def get(self):
        try:
            start = datetime.datetime.strptime(request.args['start'],
                                               "%Y-%m-%dT%H:%M:%S.%fZ")
            end = datetime.datetime.strptime(request.args['end'],
                                             "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            abort(400)

        sets = DJSet.query.\
            filter(DJSet.dtstart >= start, DJSet.dtstart <= end).\
            order_by(db.desc(DJSet.dtstart)).\
            limit(300).all()
        djsets_schema = DJSetSchema(many=True)

        return {
            'sets': djsets_schema.dump(sets),
        }


class PlaylistsTrackLogsByDateRange(Resource):
    def get(self):
        try:
            start = datetime.datetime.strptime(request.args['start'],
                                               "%Y-%m-%dT%H:%M:%S.%fZ")
            end = datetime.datetime.strptime(request.args['end'],
                                             "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            abort(400)

        tracklogs = TrackLog.query.\
            filter(TrackLog.played >= start, TrackLog.played <= end).\
            order_by(db.desc(TrackLog.id)).\
            limit(300).all()
        tracklogs_schema = TrackLogSchema(many=True)

        return {
            'tracklogs': tracklogs_schema.dump(tracklogs),
        }


class PlaylistDJs(PlaylistResource):
    def get(self):
        """
        List DJs who have played something recently.
        ---
        operationId: getPlaylistDJs
        tags:
        - trackman
        - playlists
        - dj
        """
        djs = DJ.query.order_by(DJ.airname).filter(DJ.visible == True)
        djs_schema = DJSchema(many=True)
        return {
            'djs': djs_schema.dump(djs),
        }


class PlaylistAllDJs(PlaylistResource):
    def get(self):
        """
        List all DJs, even those that haven't played anything in a while.
        ---
        operationId: getPlaylistAllDJs
        tags:
        - trackman
        - playlists
        - dj
        """
        djs = DJ.query.order_by(DJ.airname).all()
        djs_schema = DJSchema(many=True)
        return {
            'djs': djs_schema.dump(djs),
        }


class PlaylistsByDJ(PlaylistResource):
    def get(self, dj_id):
        """
        Get a list of playlists played by a particular DJ.
        ---
        operationId: getPlaylistsByDJ
        tags:
        - trackman
        - track
        parameters:
        - in: path
          name: dj_id
          type: integer
          required: true
          description: The ID of a DJ
        responses:
          404:
            description: DJ not found
        """
        dj = DJ.query.get_or_404(dj_id)
        dj_schema = DJSchema()

        sets = DJSet.query.filter(DJSet.dj_id == dj_id).order_by(
            DJSet.dtstart).all()
        djsets_schema = DJSetSchema(many=True, exclude=('dj',))

        return {
            'dj': dj_schema.dump(dj),
            'sets': djsets_schema.dump(sets),
        }


class Playlist(PlaylistResource):
    def get(self, set_id):
        """
        Get a list of tracks and archive links for a playlist.
        ---
        operationId: getPlaylist
        tags:
        - trackman
        - track
        parameters:
        - in: path
          name: set_id
          type: integer
          required: true
          description: The ID of an existing playlist
        responses:
          404:
            description: Playlist not found
        """
        djset = DJSet.query.get_or_404(set_id)
        tracks = TrackLog.query.filter(TrackLog.djset_id == djset.id).order_by(
            TrackLog.played).all()
        tracklogs_schema = TrackLogSchema(many=True)

        djset_schema = DJSetSchema()
        data = djset_schema.dump(djset)
        data.update({
            'archives': [list(a) for a in list_archives(djset)],
            'tracks': tracklogs_schema.dump(tracks),
        })
        return data


class PlaylistTrack(PlaylistResource):
    def get(self, track_id):
        """
        Get information about a Track.
        ---
        operationId: getPlaylistTrack
        tags:
        - trackman
        - track
        parameters:
        - in: path
          name: track_id
          type: integer
          required: true
          description: The ID of an existing Track
        responses:
          404:
            description: Track not found
        """
        track = Track.query.get_or_404(track_id)
        track_schema = TrackSchema()
        return track_schema.dump(track)
