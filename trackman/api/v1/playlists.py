import datetime
from flasgger import swag_from
from flask import request
from flask_restful import abort, Resource
from trackman import db, ma
from trackman.models import DJ, DJSet, Track, TrackLog
from trackman.view_utils import list_archives
from .base import PlaylistResource
from .schemas import DJSchema, DJSetSchema, TrackSchema, TrackLogSchema, \
        TrackLogLegacySchema


class NowPlaying(PlaylistResource):
    @swag_from({
        'operationId': "getNowPlaying",
        'tags': ['public', 'playlists', 'tracklog', 'track'],
        'responses': {
            200: {
                'schema': TrackLogSchema
            }
        }
    })
    def get(self):
        """Retrieve information about what is currently playing."""
        tracklog = TrackLog.query.order_by(db.desc(TrackLog.id)).first()
        tracklog_schema = TrackLogSchema()
        return tracklog_schema.dump(tracklog)


class Last15TracksSchema(ma.Schema):
    tracks = ma.Nested(TrackLogSchema, many=True)


class Last15Tracks(PlaylistResource):
    @swag_from({
        'operationId': "getLast15",
        'tags': ['public', 'playlists', 'tracklog', 'track'],
        'responses': {
            200: {
                'schema': Last15TracksSchema,
            }
        }
    })
    def get(self):
        """Retrieve information about the last 15 tracks that were played."""
        tracks = TrackLog.query.order_by(db.desc(TrackLog.id)).limit(15).all()
        schema = Last15TracksSchema()
        return schema.dump({'tracks': tracks})


class LatestTrack(PlaylistResource):
    @swag_from({
        'operationId': "getLatestTrack",
        'tags': ['public', 'playlists', 'tracklog', 'track'],
        'responses': {
            200: {
                'schema': TrackLogLegacySchema,
            }
        }
    })
    def get(self):
        """Retrieve information about what is currently playing in the old format."""
        tracklog = TrackLog.query.order_by(db.desc(TrackLog.id)).first()
        tracklog_schema = TrackLogLegacySchema()
        return tracklog_schema.dump(tracklog)


class PlaylistsByDaySchema(ma.Schema):
    dtstart = ma.DateTime()
    sets = ma.Nested(DJSetSchema, many=True)


class PlaylistsByDay(PlaylistResource):
    @swag_from({
        'operationId': "getPlaylistsByDay",
        'tags': ['public', 'playlists'],
        'parameters': [
            {
                'in': "path",
                'name': "year",
                'type': "integer",
                'required': True,
                'description': "Year",
            },
            {
                'in': "path",
                'name': "month",
                'type': "integer",
                'required': True,
                'description': "Month",
            },
            {
                'in': "path",
                'name': "day",
                'type': "integer",
                'required': True,
                'description': "Day of month",
            },
        ],
        'responses': {
            200: {
                'schema': PlaylistsByDaySchema,
            },
            404: {
                'description': "No playlists found",
            },
        },
    })
    def get(self, year, month, day):
        """Get a list of playlists played on a particular day."""
        dtstart = datetime.datetime(year, month, day, 0, 0, 0)
        dtend = datetime.datetime(year, month, day, 23, 59, 59)
        sets = DJSet.query.\
            filter(DJSet.dtstart >= dtstart, DJSet.dtstart <= dtend).\
            all()

        status_code = 200
        if len(sets) <= 0:
            # return 404 if no playlists found
            status_code = 404

        schema = PlaylistsByDaySchema()
        return schema.dump({
            'dtstart': dtstart,
            'sets': djsets_schema.dump(sets),
        }), status_code


class PlaylistsByDateRangeSchema(ma.Schema):
    sets = ma.Nested(DJSetSchema, many=True)


class PlaylistsByDateRange(Resource):
    @swag_from({
        'operationId': "getPlaylistsByDateRange",
        'tags': ['public', 'playlists'],
        'parameters': [
            {
                'in': "query",
                'name': "start",
                'type': "string",
                'required': True,
                'description': "Start timestamp in ISO format",
            },
            {
                'in': "query",
                'name': "end",
                'type': "string",
                'required': True,
                'description': "End timestamp in ISO format",
            },
        ],
        'responses': {
            200: {
                'schema': PlaylistsByDateRangeSchema,
            },
        },
    })
    def get(self):
        """Get a list of playlists played between particular times."""
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

        schema = PlaylistsByDateRangeSchema()
        return schema.dump({
            'sets': sets,
        })


class PlaylistsTrackLogsByDateRangeSchema(ma.Schema):
    tracklogs = ma.Nested(TrackLogSchema, many=True)


class PlaylistsTrackLogsByDateRange(Resource):
    @swag_from({
        'operationId': "getPlaylistsTrackLogsByDateRange",
        'tags': ['public', 'playlists'],
        'parameters': [
            {
                'in': "query",
                'name': "start",
                'type': "string",
                'required': True,
                'description': "Start timestamp in ISO format",
            },
            {
                'in': "query",
                'name': "end",
                'type': "string",
                'required': True,
                'description': "End timestamp in ISO format",
            },
        ],
        'responses': {
            200: {
                'schema': PlaylistsTrackLogsByDateRangeSchema,
            },
        },
    })
    def get(self):
        """Get a list of tracks played between particular times."""
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

        schema = PlaylistsTrackLogsByDateRangeSchema()
        return schema.dump({
            'tracklogs': tracklogs,
        })


class PlaylistDJsSchema(ma.Schema):
    djs = ma.Nested(DJSchema, many=True)


class PlaylistDJs(PlaylistResource):
    @swag_from({
        'operationId': "getPlaylistDJs",
        'tags': ['public', 'dj'],
    })
    def get(self):
        """List DJs who have played something recently."""
        djs = DJ.query.order_by(DJ.airname).filter(DJ.visible == True)
        schema = PlaylistDJsSchema()
        schema.dump({
            'djs': djs_schema.dump(djs),
        })


class PlaylistAllDJs(PlaylistResource):
    @swag_from({
        'operationId': "getPlaylistAllDJs",
        'tags': ['public', 'dj'],
    })
    def get(self):
        """List all DJs, even those that haven't played anything in a while."""
        djs = DJ.query.order_by(DJ.airname).all()
        schema = PlaylistDJsSchema()
        schema.dump({
            'djs': djs_schema.dump(djs),
        })


class PlaylistsByDJSchema(ma.Schema):
    dj = ma.Nested(DJSchema)
    sets = ma.Nested(lambda: DJSetSchema(exclude=('dj',), many=True))


class PlaylistsByDJ(PlaylistResource):
    @swag_from({
        'operationId': "getPlaylistsByDJ",
        'tags': ['public', 'playlists'],
        'parameters': [
            {
                'in': "path",
                'name': "dj_id",
                'type': "integer",
                'required': True,
                'description': "The ID of a DJ",
            }
        ],
        'responses': {
            200: {
                'schema': PlaylistsByDJSchema,
            },
            404: {
                'description': "DJ not found",
            },
        },
    })
    def get(self, dj_id):
        """Get a list of playlists played by a particular DJ."""
        dj = DJ.query.get_or_404(dj_id)
        sets = DJSet.query.filter(DJSet.dj_id == dj_id).order_by(
            DJSet.dtstart).all()

        schema = PlaylistsByDJSchema()
        schema.dump({
            'dj': dj,
            'sets': sets,
        })


class PlaylistSchema(DJSetSchema):
    archives = ma.List(ma.List(ma.String))
    tracks = ma.Nested(TrackLogSchema, many=True)


class Playlist(PlaylistResource):
    @swag_from({
        'operationId': "getPlaylist",
        'tags': ['public', 'playlists', 'track'],
        'parameters': [
            {
                'in': "path",
                'name': "set_id",
                'type': "integer",
                'required': True,
                'description': "The ID of an existing playlist",
            },
        ],
        'responses': {
            200: {
                'schema': PlaylistSchema,
            },
            404: {
                'description': "Playlist not found",
            },
        },
    })
    def get(self, set_id):
        """Get a list of tracks and archive links for a playlist."""
        djset = DJSet.query.get_or_404(set_id)
        tracks = TrackLog.query.filter(TrackLog.djset_id == djset.id).order_by(
            TrackLog.played).all()

        djset.archives = [list(a) for a in list_archives(djset)]
        djset.tracks = tracks

        schema = PlaylistSchema()
        return schema.dump(djset)


class PlaylistTrack(PlaylistResource):
    @swag_from({
        'operationId': "getPlaylistTrack",
        'tags': ['public', 'track'],
        'parameters': [
            {
                'in': 'path',
                'name': 'track_id',
                'type': 'integer',
                'required': True,
                'description': "The ID of an existing track",
            },
        ],
        'responses': {
            200: {
                'schema': TrackSchema,
            },
            404: {
                'description': "Track not found",
            },
        },
    })
    def get(self, track_id):
        """Get information about a track."""
        track = Track.query.get_or_404(track_id)
        track_schema = TrackSchema()
        return track_schema.dump(track)
