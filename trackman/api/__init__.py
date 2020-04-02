from flask import Blueprint, json, make_response
from flask_cors import CORS
from flask_restful import Api

from .v1.airlog import AirLog, AirLogList
from .v1.autologout import AutologoutControl
from .v1.automation import AutomationLog
from .v1.dj import DJ
from .v1.djset import DJSet, DJSetEnd, DJSetList
from .v1.rotation import RotationList
from .v1.track import Track, TrackReport, TrackSearch, TrackAutoComplete, \
    TrackList
from .v1.tracklog import TrackLog, TrackLogList
from .v1.charts import Charts, AlbumCharts, DJAlbumCharts, ArtistCharts, \
    DJArtistCharts, TrackCharts, DJTrackCharts, DJSpinCharts, DJVinylSpinCharts
from .v1.playlists import NowPlaying, Last15Tracks, LatestTrack, \
    PlaylistsByDay, PlaylistsByDateRange, PlaylistsTrackLogsByDateRange, \
    PlaylistDJs, PlaylistAllDJs, PlaylistsByDJ, Playlist, PlaylistTrack
from .v1.internal import InternalPing


api_bp = Blueprint('trackman_api', __name__)
CORS(api_bp, resources={
    r"/api/now_playing": {"origins": "*"},
    r"/api/playlists/*": {"origins": "*"},
    r"/api/charts/*": {"origins": "*"},
})

errors = {
    'IPAccessDeniedException': {
        'success': False,
        'message': "Forbidden",
        'status': 403,
    },
}

api = Api(api_bp, errors=errors)
api.add_resource(AutomationLog, '/api/automation/log')
api.add_resource(DJ, '/api/dj/<int:dj_id>')
api.add_resource(DJSet, '/api/djset/<int:djset_id>')
api.add_resource(DJSetEnd, '/api/djset/<int:djset_id>/end')
api.add_resource(DJSetList, '/api/djset')
api.add_resource(Track, '/api/track/<int:track_id>')
api.add_resource(TrackReport, '/api/track/<int:track_id>/report')
api.add_resource(TrackSearch, '/api/search')
api.add_resource(TrackAutoComplete, '/api/autocomplete')
api.add_resource(TrackList, '/api/track')
api.add_resource(TrackLog, '/api/tracklog/edit/<int:tracklog_id>')
api.add_resource(TrackLogList, '/api/tracklog')
api.add_resource(AutologoutControl, '/api/autologout')
api.add_resource(AirLog, '/api/airlog/edit/<int:airlog_id>')
api.add_resource(AirLogList, '/api/airlog')
api.add_resource(RotationList, '/api/rotations')
api.add_resource(Charts, '/api/charts')
api.add_resource(AlbumCharts,
                 '/api/charts/albums',
                 '/api/charts/albums/<string:period>',
                 '/api/charts/albums/<string:period>/<int:year>',
                 '/api/charts/albums/<string:period>/<int:year>/<int:month>')
api.add_resource(DJAlbumCharts, '/api/charts/dj/<int:dj_id>/albums')
api.add_resource(ArtistCharts,
                 '/api/charts/artists',
                 '/api/charts/artists/<string:period>',
                 '/api/charts/artists/<string:period>/<int:year>',
                 '/api/charts/artists/<string:period>/<int:year>/<int:month>')
api.add_resource(DJArtistCharts, '/api/charts/dj/<int:dj_id>/artists')
api.add_resource(TrackCharts,
                 '/api/charts/tracks',
                 '/api/charts/tracks/<string:period>',
                 '/api/charts/tracks/<string:period>/<int:year>',
                 '/api/charts/tracks/<string:period>/<int:year>/<int:month>')
api.add_resource(DJTrackCharts, '/api/charts/dj/<int:dj_id>/tracks')
api.add_resource(DJSpinCharts, '/api/charts/dj/spins')
api.add_resource(DJVinylSpinCharts, '/api/charts/dj/vinyl_spins')
api.add_resource(NowPlaying, '/api/now_playing')
api.add_resource(Last15Tracks, '/api/playlists/last15')
api.add_resource(LatestTrack, '/api/playlists/latest_track')
api.add_resource(PlaylistsTrackLogsByDateRange,
                 '/api/playlists/tracklogs/date/range')
api.add_resource(PlaylistsByDay,
                 '/api/playlists/date/<int:year>/<int:month>/<int:day>')
api.add_resource(PlaylistsByDateRange, '/api/playlists/date/range')
api.add_resource(PlaylistDJs, '/api/playlists/dj')
api.add_resource(PlaylistAllDJs, '/api/playlists/dj/all')
api.add_resource(PlaylistsByDJ, '/api/playlists/dj/<int:dj_id>')
api.add_resource(Playlist, '/api/playlists/set/<int:set_id>')
api.add_resource(PlaylistTrack, '/api/playlists/track/<int:track_id>')
api.add_resource(InternalPing, '/api/internal/ping')


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp
