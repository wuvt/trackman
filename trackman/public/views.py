from flask import (
        current_app, make_response, render_template,
        redirect, request, url_for, Response,
)
import datetime
import re
from feedwerk.atom import AtomFeed

from ..api.v1.charts import (
        AlbumCharts,
        DJAlbumCharts,
        ArtistCharts,
        DJArtistCharts,
        TrackCharts,
        DJTrackCharts,
        DJSpinCharts,
        DJVinylSpinCharts,
)
from ..api.v1.playlists import (
        NowPlaying,
        Last15Tracks,
        LatestTrack,
        PlaylistsByDay,
        PlaylistDJs,
        PlaylistAllDJs,
        PlaylistsByDJ,
        Playlist,
        PlaylistTrack,
)
from . import bp
from .view_utils import make_external


#############################################################################
# Playlist Information
#############################################################################


@bp.route('/playlists')
def playlists_index():
    track = NowPlaying().get()
    return render_template('public/index.html', track=track)


@bp.route('/last15')
def last15():
    result = Last15Tracks().get()
    return render_template('public/last15.html', tracklogs=result['tracks'])


@bp.route('/last15.atom')
def last15_feed():
    result = Last15Tracks().get()
    tracks = result['tracks']
    feed = AtomFeed(
        "{0}: Last 15 Tracks".format(current_app.config['TRACKMAN_NAME']),
        feed_url=request.url,
        url=make_external(url_for('.last15')))

    for tracklog in tracks:
        feed.add(
            "{artist}: '{title}'".format(
                artist=tracklog['track']['artist'],
                title=tracklog['track']['title']),
            "'{title}' by {artist} on {album} spun by {dj}".format(
                album=tracklog['track']['album'],
                artist=tracklog['track']['artist'],
                title=tracklog['track']['title'],
                dj=tracklog['dj']['airname']),
            url=make_external(url_for('.playlist',
                                      set_id=tracklog['djset_id'],
                                      _anchor="t{}".format(tracklog['id']))),
            author=tracklog['dj']['airname'],
            updated=tracklog['played'],
            published=tracklog['played'])

    return feed.get_response()


@bp.route('/playlists/latest_track')
def latest_track():
    track = LatestTrack().get()
    return Response("{artist} - {title}".format(**track),
                    mimetype="text/plain")


@bp.route('/playlists/latest_track_clean')
def latest_track_clean():
    naughty_word_re = re.compile(
        r'shit|piss|fuck|cunt|cocksucker|tits|twat|asshole',
        re.IGNORECASE)

    track = LatestTrack().get()
    for k, v in list(track.items()):
        if type(v) == str or type(v) == str:
            track[k] = naughty_word_re.sub('****', v)

    output = "{artist} - {title} [DJ: {dj}]".format(**track)
    return Response(output, mimetype="text/plain")


@bp.route('/playlists/latest_track_stream')
def latest_track_stream():
    track = LatestTrack().get()
    return Response("""\
title={title}
artist={artist}
album={album}
description={description}
contact={contact}
""".format(**track), mimetype="text/plain")


# Playlist Archive (by date) {{{
@bp.route('/playlists/date')
def playlists_date():
    today = datetime.datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0)
    return render_template('public/playlists_date_list.html', today=today)


@bp.route('/js/playlists_by_date_init.js')
def playlists_by_date_init_js():
    resp = make_response(render_template('playlists_by_date_init.js'))
    resp.headers['Content-Type'] = "application/javascript; charset=utf-8"
    return resp


@bp.route('/playlists/date/<int:year>/<int:month>/<int:day>')
def playlists_date_sets(year, month, day):
    results, status_code = PlaylistsByDay().get(year, month, day)

    now = datetime.datetime.utcnow()
    start_date = results['dtstart'].replace(tzinfo=None)
    next_date = start_date + datetime.timedelta(hours=24)
    next_url = url_for('.playlists_date_sets', year=next_date.year,
                       month=next_date.month, day=next_date.day)
    if next_date > now:
        next_url = None

    if start_date < now:
        prev_date = start_date - datetime.timedelta(hours=24)
        prev_url = url_for('.playlists_date_sets', year=prev_date.year,
                           month=prev_date.month, day=prev_date.day)
    else:
        prev_url = None

    results.update({
        'prev_url': prev_url,
        'next_url': next_url,
    })

    return render_template(
        'public/playlists_date_sets.html',
        date=results['dtstart'],
        sets=results['sets'],
        prev_url=results['prev_url'],
        next_url=results['next_url']), status_code


@bp.route('/playlists/date/jump', methods=['POST'])
def playlists_date_jump():
    jumpdate = datetime.datetime.strptime(request.form['date'], "%Y-%m-%d")
    return redirect(url_for('.playlists_date_sets', year=jumpdate.year,
                            month=jumpdate.month, day=jumpdate.day))
# }}}


# Playlist Archive (by DJ) {{{
@bp.route('/playlists/dj')
def playlists_dj():
    results = PlaylistDJs().get()
    return render_template('public/playlists_dj_list.html', djs=results['djs'])


@bp.route('/playlists/dj/all')
def playlists_dj_all():
    results = PlaylistAllDJs().get()
    return render_template('public/playlists_dj_list_all.html',
                           djs=results['djs'])


@bp.route('/playlists/dj/<int:dj_id>')
def playlists_dj_sets(dj_id):
    results = PlaylistsByDJ().get(dj_id)
    return render_template('public/playlists_dj_sets.html',
                           dj=results['dj'], sets=results['sets'])
# }}}


# Charts {{{
@bp.route('/playlists/charts')
def charts_index():
    periodic_charts = [
        ('.charts_albums', "Top albums"),
        ('.charts_artists', "Top artists"),
        ('.charts_tracks', "Top tracks"),
    ]
    return render_template('public/charts.html', periodic_charts=periodic_charts)


@bp.route('/playlists/charts/albums')
@bp.route('/playlists/charts/albums/<string:period>')
@bp.route('/playlists/charts/albums/<string:period>/<int:year>')
@bp.route('/playlists/charts/albums/<string:period>/<int:year>/<int:month>')
def charts_albums(period=None, year=None, month=None):
    if period == 'dj' and year is not None:
        return redirect(url_for('.charts_albums_dj', dj_id=year))

    results = AlbumCharts().get(period, year, month)
    return render_template('public/chart_albums.html',
                           start=results['start'],
                           end=results['end'],
                           results=results['results'])


@bp.route('/playlists/charts/dj/<int:dj_id>/albums')
def charts_albums_dj(dj_id):
    results = DJAlbumCharts().get(dj_id)
    return render_template('public/chart_albums_dj.html',
                           dj=results['dj'],
                           results=results['results'])


@bp.route('/playlists/charts/artists')
@bp.route('/playlists/charts/artists/<string:period>')
@bp.route('/playlists/charts/artists/<string:period>/<int:year>')
@bp.route('/playlists/charts/artists/<string:period>/<int:year>/<int:month>')
def charts_artists(period=None, year=None, month=None):
    if period == 'dj' and year is not None:
        return redirect(url_for('.charts_artists_dj', dj_id=year))

    results = ArtistCharts().get(period, year, month)
    return render_template('public/chart_artists.html',
                           start=results['start'],
                           end=results['end'],
                           results=results['results'])


@bp.route('/playlists/charts/dj/<int:dj_id>/artists')
def charts_artists_dj(dj_id):
    results = DJArtistCharts().get(dj_id)
    return render_template('public/chart_artists_dj.html',
                           dj=results['dj'],
                           results=results['results'])


@bp.route('/playlists/charts/tracks')
@bp.route('/playlists/charts/tracks/<string:period>')
@bp.route('/playlists/charts/tracks/<string:period>/<int:year>')
@bp.route('/playlists/charts/tracks/<string:period>/<int:year>/<int:month>')
def charts_tracks(period=None, year=None, month=None):
    if period == 'dj' and year is not None:
        return redirect(url_for('.charts_tracks_dj', dj_id=year))

    results = TrackCharts().get(period, year, month)
    return render_template('public/chart_tracks.html',
                           start=results['start'],
                           end=results['end'],
                           results=results['results'])


@bp.route('/playlists/charts/dj/<int:dj_id>/tracks')
def charts_tracks_dj(dj_id):
    results = DJTrackCharts().get(dj_id)
    return render_template('public/chart_tracks_dj.html',
                           dj=results['dj'],
                           results=results['results'])


@bp.route('/playlists/charts/dj/spins')
def charts_dj_spins():
    results = DJSpinCharts().get()
    return render_template('public/chart_dj_spins.html',
                           results=results['results'])


@bp.route('/playlists/charts/dj/vinyl_spins')
def charts_dj_vinyl_spins():
    results = DJVinylSpinCharts().get()
    return render_template('public/chart_dj_vinyl_spins.html',
                           results=results['results'])
# }}}


@bp.route('/playlists/set/<int:set_id>')
def playlist(set_id):
    results = Playlist().get(set_id)
    return render_template('public/playlist.html',
                           archives=results['archives'],
                           djset=results,
                           tracklogs=results['tracks'])


@bp.route('/playlists/track/<int:track_id>')
def playlists_track(track_id):
    results = PlaylistTrack().get(track_id)
    return render_template('public/playlists_track.html',
                           track=results,
                           tracklogs=results['plays'])
