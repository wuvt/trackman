DEBUG = False
# SESSION_COOKIE_SECURE = True

SQLALCHEMY_TRACK_MODIFICATIONS = False
REDIS_URL = 'redis://redis:6379/0'

ARTISTS_PER_PAGE = 500

STATION_NAME = "WUVT-FM 90.7 Blacksburg, VA"
STATION_URL = "https://www.wuvt.vt.edu"

# DJ activity timer for automation/DJ logout in seconds
DJ_TIMEOUT = 30 * 60
EXTENDED_DJ_TIMEOUT = 120 * 60
NO_DJ_TIMEOUT = 5 * 60

CLAIM_TOKEN_TIMEOUT = 86400

AUTOMATION_PASSWORD = ""
ICECAST_URL = ""
ICECAST_MOUNTS = []
INTERNAL_IPS = ['127.0.0.1/8']
TRACKMAN_NAME = "Trackman"
TRACKMAN_ARTIST_PROHIBITED = ["?", "-"]
TRACKMAN_LABEL_PROHIBITED = ["?", "-", "same"]
TRACKMAN_DJ_HIDE_AFTER_DAYS = 425

ARCHIVE_URL_FORMAT = ""
MUSICBRAINZ_HOSTNAME = "musicbrainz.org"
MUSICBRAINZ_RATE_LIMIT = 1.0

MAIL_FROM = "noreply@localhost"
SMTP_SERVER = "mailhog"
SMTP_PORT = 1025
SMTP_TLS = False
SMTP_USER = ""
SMTP_PASSWORD = ""
CHART_MAIL = False
CHART_MAIL_DEST = "charts@localhost"

PROXY_FIX = False
PROXY_FIX_NUM_PROXIES = 1

# Allow CSRF tokens to last for 31 days
WTF_CSRF_TIME_LIMIT = 2678400

AUTH_SUPERADMINS = []
AUTH_ROLE_GROUPS = {
    'admin': ['webmasters'],
    'library': ['librarians'],
    'dj': ['djs'],
}

PUBSUB_PUB_URL_ALL = "http://nginx:8080/pub"
PUBSUB_PUB_URL_DJ = "http://nginx:8080/dj/pub"

SENTRY_DSN = ""
