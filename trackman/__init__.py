from dateutil import tz
from flask import Flask, Request
from flask_caching import Cache
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import humanize
import os
import redis
from . import defaults
import uuid
import datetime
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

try:
    import uwsgi
except ImportError:
    pass

json_mimetypes = ['application/json']


def localize_datetime(fromtime):
    return fromtime.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())


def format_datetime(value, format=None):
    value = localize_datetime(value)
    return value.strftime(format or "%Y-%m-%d %H:%M:%S %z")


def format_isodatetime(value):
    if value.utcoffset() is None:
        value = value.replace(tzinfo=tz.tzutc())

    return value.isoformat()


def format_currency(value):
    return "${:,.2f}".format(value)


def format_uuid(value):
    try:
        return uuid.UUID(value)
    except ValueError:
        return None


class JSONRequest(Request):
    # from http://flask.pocoo.org/snippets/45/
    def wants_json(self):
        mimes = json_mimetypes
        mimes.append('text/html')
        best = self.accept_mimetypes.best_match(mimes)
        return best in json_mimetypes and \
            self.accept_mimetypes[best] > \
            self.accept_mimetypes['text/html']


app = Flask(__name__)
app.config.from_object(defaults)

# use the value of the SQLALCHEMY_DATABASE_URI environment variable as the
# default; any value specified in the config will override this
app.config.setdefault('SQLALCHEMY_DATABASE_URI',
                      os.getenv('SQLALCHEMY_DATABASE_URI'))

config_path = os.environ.get('APP_CONFIG_PATH', 'config.py')
if config_path.endswith('.py'):
    app.config.from_pyfile(config_path, silent=True)
else:
    app.config.from_json(config_path, silent=True)

app.request_class = JSONRequest
app.jinja_env.filters.update({
    'intcomma': humanize.intcomma,
    'intword': humanize.intword,
    'naturalday': humanize.naturalday,
    'naturaldate': humanize.naturaldate,
    'naturaltime': humanize.naturaltime,
    'naturalsize': humanize.naturalsize,

    'datetime': format_datetime,
    'isodatetime': format_isodatetime,
    'format_currency': format_currency,
    'uuid': format_uuid,
})
app.static_folder = 'static'

if app.config['PROXY_FIX']:
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app,
                            x_for=app.config['PROXY_FIX_NUM_PROXIES'],
                            x_proto=app.config['PROXY_FIX_NUM_PROXIES'],
                            x_host=app.config['PROXY_FIX_NUM_PROXIES'],
                            x_prefix=app.config['PROXY_FIX_NUM_PROXIES'])

redis_conn = redis.from_url(app.config['REDIS_URL'])

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from trackman.auth import AuthManager, current_user
auth_manager = AuthManager()
auth_manager.init_app(app, db)

if len(app.config['SENTRY_DSN']) > 0:
    sentry_sdk.init(
        app.config['SENTRY_DSN'],
        integrations=[
            FlaskIntegration(),
            RedisIntegration(),
            SqlalchemyIntegration(),
        ])


@app.context_processor
def inject_year():
    return {'year': datetime.date.today().strftime("%Y")}


@app.after_request
def add_app_user_logvar(response):
    if uwsgi is not None and current_user.is_authenticated:
        uwsgi.set_logvar('app_user', current_user.sub)
    return response


playlists_cache = Cache(config={
    'CACHE_KEY_PREFIX': "trackman_playlists_",
})
charts_cache = Cache(config={
    'CACHE_DEFAULT_TIMEOUT': 14400,
    'CACHE_KEY_PREFIX': "trackman_charts_",
})


if app.debug:
    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)


def init_app():
    from trackman import admin
    app.register_blueprint(admin.bp, url_prefix='/admin')

    from . import admin_views, cli, models, views
    from .api import api, api_bp
    from .library import library_bp
    from .library import views as library_views

    from .blueprints import private_bp
    app.register_blueprint(private_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(library_bp, url_prefix='/library')

    from .public import bp as public_bp
    app.register_blueprint(public_bp)

    cache_redis_url = app.config.get('CACHE_REDIS_URL',
                                     app.config['REDIS_URL'])
    playlists_cache.init_app(app, config={
        'CACHE_TYPE': "RedisCache",
        'CACHE_REDIS_URL': cache_redis_url,
    })
    charts_cache.init_app(app, config={
        'CACHE_TYPE': "RedisCache",
        'CACHE_REDIS_URL': cache_redis_url,
    })


init_app()
