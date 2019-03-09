from flask import Flask, Request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy as FlaskSQLAlchemy
from flask_wtf.csrf import CSRFProtect
import humanize
import os
from . import defaults, filters
from .kv import KVStore
import datetime
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

json_mimetypes = ['application/json']


class JSONRequest(Request):
    # from http://flask.pocoo.org/snippets/45/
    def wants_json(self):
        mimes = json_mimetypes
        mimes.append('text/html')
        best = self.accept_mimetypes.best_match(mimes)
        return best in json_mimetypes and \
            self.accept_mimetypes[best] > \
            self.accept_mimetypes['text/html']


class SQLAlchemy(FlaskSQLAlchemy):
    """
    A hack because flask-sqlalchemy hasn't fixed this yet:
    https://github.com/mitsuhiko/flask-sqlalchemy/issues/166
    """
    def apply_driver_hacks(self, app, info, options):
        if not options:
            options = {}
        if 'pool_pre_ping' not in options:
            options['pool_pre_ping'] = True
        return super(SQLAlchemy, self).apply_driver_hacks(app, info, options)


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

    'datetime': filters.format_datetime,
    'isodatetime': filters.format_isodatetime,
    'format_currency': filters.format_currency,
    'uuid': filters.format_uuid,
})
app.static_folder = 'static'

if app.config['PROXY_FIX']:
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app,
                            num_proxies=app.config['PROXY_FIX_NUM_PROXIES'])

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
kv = KVStore(app)

from trackman.auth import AuthManager
auth_manager = AuthManager()
auth_manager.db = db
auth_manager.init_app(app)

from trackman.auth.oidc import OpenIDConnect
oidc = OpenIDConnect(app)

if len(app.config['SENTRY_DSN']) > 0:
    sentry_sdk.init(app.config['SENTRY_DSN'],
                    integrations=[FlaskIntegration()])


@app.context_processor
def inject_year():
    return {'year': datetime.date.today().strftime("%Y")}


if app.debug:
    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)


def init_app():
    from trackman import admin
    app.register_blueprint(admin.bp, url_prefix='/admin')

    from trackman import auth
    from trackman.auth import views as auth_views
    app.register_blueprint(auth.bp, url_prefix='/auth')

    from . import admin_views, cli, models, views
    from .api import api, api_bp
    from .library import library_bp
    from .library import views as library_views

    from .blueprints import private_bp
    app.register_blueprint(private_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(library_bp, url_prefix='/library')


init_app()
