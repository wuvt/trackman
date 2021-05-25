from flask_restful import Resource
from trackman import csrf, playlists_cache, charts_cache
from trackman.view_utils import ajax_only, local_only, dj_only, dj_interact, \
    require_dj_session, require_onair


class TrackmanResource(Resource):
    decorators = [csrf.exempt]
    method_decorators = [dj_only, ajax_only, dj_interact,
                         require_dj_session]


class TrackmanOnAirResource(TrackmanResource):
    method_decorators = [dj_only, ajax_only, dj_interact,
                         require_dj_session, require_onair]


class TrackmanDJResource(TrackmanResource):
    method_decorators = [dj_only, ajax_only, dj_interact]


class TrackmanStudioResource(TrackmanResource):
    method_decorators = [local_only, ajax_only, dj_interact]


class PlaylistResource(Resource):
    method_decorators = {
        'get': [
            playlists_cache.memoize(args_to_ignore=['self', 'cls']),
        ],
    }


class ChartResource(Resource):
    method_decorators = {
        'get': [
            charts_cache.memoize(args_to_ignore=['self', 'cls']),
        ],
    }
