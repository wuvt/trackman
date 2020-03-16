from trackman import app, pubsub, playlists_cache
from trackman.signals import tracklog_added, tracklog_deleted, \
        tracklog_modified, track_db_changed, airlog_added, airlog_deleted, \
        airlog_modified, dj_session_started, dj_session_ended
from trackman.api.v1.schemas import TrackLogModifiedSchema


tracklog_schema = TrackLogModifiedSchema()


def process_tracklog_event(event, tracklog):
    playlists_cache.clear()

    pubsub.publish(
        app.config['PUBSUB_PUB_URL_ALL'],
        message={
            'event': event,
            'tracklog': tracklog_schema.dump(tracklog),
        })


@tracklog_added.connect_via(app)
def when_tracklog_added(sender, tracklog):
    process_tracklog_event('track_change', tracklog)


@tracklog_deleted.connect_via(app)
def when_tracklog_deleted(sender, tracklog=None):
    process_tracklog_event('track_delete', tracklog)


@tracklog_modified.connect_via(app)
def when_tracklog_modified(sender, tracklog):
    process_tracklog_event('track_edit', tracklog)


@track_db_changed.connect_via(app)
def when_track_db_changed(sender):
    playlists_cache.clear()


@airlog_added.connect_via(app)
def when_airlog_added(sender, airlog):
    playlists_cache.clear()


@airlog_deleted.connect_via(app)
def when_airlog_deleted(sender, airlog=None):
    playlists_cache.clear()


@airlog_modified.connect_via(app)
def when_airlog_modified(sender, airlog):
    playlists_cache.clear()


@dj_session_started.connect_via(app)
def when_dj_session_started(sender, djset):
    playlists_cache.clear()


@dj_session_ended.connect_via(app)
def when_dj_session_ended(sender, djset=None):
    playlists_cache.clear()
    pubsub.publish(
        app.config['PUBSUB_PUB_URL_DJ'],
        message={
            'event': "session_end",
        })
