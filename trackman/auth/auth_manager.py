import base64
import datetime
import os
from flask import (
    abort,
    make_response,
    redirect,
    request,
    session,
    url_for,
    _request_ctx_stack,
)
from functools import wraps

from .base import AuthDataStore
from .mixins import AnonymousUserMixin, UserMixin
from .utils import (
    current_user,
    current_user_roles,
    _user_context_processor,
    _user_roles_context_processor,
)


class AuthManager(object):
    def __init__(self, app=None, datastore: AuthDataStore = None):
        self.all_roles = set()

        self.exempt_methods = set(["OPTIONS"])

        if app is not None and datastore is not None:
            self.init_app(app, datastore)

    def init_app(self, app, datastore: AuthDataStore):
        self.app = app
        self.datastore = datastore

        app.auth_manager = self
        app.context_processor(_user_context_processor)
        app.context_processor(_user_roles_context_processor)

        if app.config.get("AUTH_METHOD") == "google":
            app.config.setdefault("GOOGLE_ALLOWED_DOMAINS", [])

            from authlib.integrations.flask_client import OAuth

            self.oauth = OAuth(app)

            from loginpass import create_flask_blueprint
            from loginpass.google import Google
            from .google import handle_authorize

            google_bp = create_flask_blueprint([Google], self.oauth, handle_authorize)
            app.register_blueprint(google_bp, url_prefix="/auth")

            self.login_view = "loginpass.login"
            self.login_view_kwargs = {"name": "google"}
        else:
            from authlib.integrations.flask_client import OAuth

            self.oauth = OAuth(app)

            from loginpass import create_flask_blueprint
            from .oidc import create_oidc_backend, handle_authorize

            backend = create_oidc_backend(
                "oidc", app.config["OIDC_CLIENT_SECRETS"], app.config.get("OIDC_SCOPES")
            )
            oidc_bp = create_flask_blueprint([backend], self.oauth, handle_authorize)
            app.register_blueprint(oidc_bp, url_prefix="/auth")

            self.login_view = "loginpass.login"
            self.login_view_kwargs = {"name": "oidc"}

        from . import views

        app.register_blueprint(views.bp, url_prefix="/auth")

    def generate_session_token(self):
        return base64.urlsafe_b64encode(os.urandom(64)).decode("ascii")

    def load_user_session(self):
        ctx = _request_ctx_stack.top

        session_token = session.get("user_session_token")
        if session_token is None or type(session_token) != str:
            ctx.user = AnonymousUserMixin()
            ctx.user_roles = set([])
        else:
            now = datetime.datetime.utcnow()
            user_session = self.datastore.get_session_by_token(session_token)
            if (
                user_session is not None
                and now > user_session.login_at
                and now < user_session.expires
            ):
                ctx.user = user_session.user
                ctx.user_roles = user_session.roles

                # update remote address for session if it has changed
                if user_session.remote_addr != request.remote_addr:
                    user_session.remote_addr = request.remote_addr
                    self.datastore.commit()
            else:
                ctx.user = AnonymousUserMixin()
                ctx.user_roles = set([])

    def unauthorized(self):
        session["login_target"] = request.url
        return redirect(url_for(self.login_view, **self.login_view_kwargs))

    def check_access(self, *roles):
        roles = set(roles)
        self.all_roles.update(roles)

        def access_decorator(f):
            @wraps(f)
            def access_wrapper(*args, **kwargs):
                if request.method in self.exempt_methods:
                    return f(*args, **kwargs)
                elif not current_user.is_authenticated:
                    return self.unauthorized()

                if roles.isdisjoint(current_user_roles):
                    abort(403)

                resp = make_response(f(*args, **kwargs))
                resp.cache_control.no_cache = True
                resp.cache_control.no_store = True
                resp.cache_control.must_revalidate = True
                return resp

            return access_wrapper

        return access_decorator

    def login_user(self, user: UserMixin, roles: list):
        session_token = self.generate_session_token()
        user_session = self.datastore.create_session(
            session_token=session_token,
            user=user,
            expires=datetime.datetime.utcnow() + self.app.permanent_session_lifetime,
            user_agent=str(request.user_agent),
            remote_addr=request.remote_addr,
            roles=roles,
        )

        session["user_session_token"] = session_token
        _request_ctx_stack.top.user = user_session.user
        _request_ctx_stack.top.user_roles = user_session.roles
        return True

    def logout_user(self):
        session_token = session.pop("user_session_token", None)
        if session_token is not None or type(session_token) != str:
            self.datastore.delete_session_by_token(session_token)

        _request_ctx_stack.top.user = AnonymousUserMixin()
        _request_ctx_stack.top.user_roles = set([])
        return True

    def end_all_sessions_for_user(self, sub: str):
        self.datastore.delete_sessions_for_user(sub)
        return True

    def cleanup_expired_sessions(self):
        self.datastore.delete_sessions_by_expiration(datetime.datetime.utcnow())

    def get_user_roles(self, user: UserMixin, user_groups: list = None):
        if user.sub in self.app.config["AUTH_SUPERADMINS"]:
            return list(self.all_roles)

        user_roles = set([])

        if user_groups is not None:
            for role, groups in list(self.app.config["AUTH_ROLE_GROUPS"].items()):
                for group in groups:
                    if group in user_groups:
                        user_roles.add(role)

            user_roles.update(self.datastore.get_roles_for_groups(user_groups))

        user_roles.update(self.datastore.get_roles_for_user(user.sub))

        return list(user_roles)
