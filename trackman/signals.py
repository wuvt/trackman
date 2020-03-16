from blinker import Namespace

signals = Namespace()

tracklog_added = signals.signal('tracklog-added')
tracklog_deleted = signals.signal('tracklog-deleted')
tracklog_modified = signals.signal('tracklog-modified')

track_db_changed = signals.signal('track-db-changed')

airlog_added = signals.signal('airlog-added')
airlog_deleted = signals.signal('airlog-deleted')
airlog_modified = signals.signal('airlog-modified')

dj_session_started = signals.signal('dj-session-started')
dj_session_ended = signals.signal('dj-session-ended')
