from flask import abort, g, get_flashed_messages, redirect, \
        render_template, request, url_for, session

from trackman import app, auth_manager, oidc
from trackman.auth import login_required, login_user, logout_user
from trackman.auth.blueprint import bp
from trackman.auth.models import User, UserRole, GroupRole
from trackman.auth.view_utils import log_auth_success, log_auth_failure
from trackman.view_utils import is_safe_url


def get_user_roles(user, user_groups=None):
    if user.sub in app.config['AUTH_SUPERADMINS']:
        return list(auth_manager.all_roles)

    user_roles = set([])

    if user_groups is not None:
        for role, groups in list(app.config['AUTH_ROLE_GROUPS'].items()):
            for group in groups:
                if group in user_groups:
                    user_roles.add(role)

        for group in user_groups:
            group_roles_db = GroupRole.query.filter(GroupRole.group == group)
            for entry in group_roles_db:
                user_roles.add(entry.role)

    user_roles_db = UserRole.query.filter(UserRole.sub == user.sub)
    for entry in user_roles_db:
        user_roles.add(entry.role)

    return list(user_roles)


@bp.route('/oidc_callback')
def oidc_callback():
    response = oidc.oidc._oidc_callback()

    id_token = getattr(g, 'oidc_id_token', None)
    if id_token is None:
        log_auth_failure("oidc", None)
        abort(401)

    if 'email' not in id_token:
        return render_template('auth/need_email.html'), 400

    user = User(id_token)
    user_groups = id_token.get(app.config.get('OIDC_GROUPS_CLAIM', 'groups'))
    login_user(user, get_user_roles(user, user_groups))

    log_auth_success("oidc", user.sub)
    return response


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # pull all flashed messages off the session, otherwise they will be
    # displayed post login, which is not what we want
    get_flashed_messages()

    target = request.values.get('next', '')
    if not target or not is_safe_url(target):
        target = url_for('admin.index')

    return oidc.oidc.redirect_to_auth_server(target)


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('access', None)

    return redirect('/')
