import googleapiclient.discovery
from flask import abort, current_app
from google.oauth2 import service_account
from .models import User
from .utils import login_user, get_user_roles
from .view_utils import log_auth_success, log_auth_failure, redirect_back


def get_groups(user_info):
    credentials = service_account.Credentials.from_service_account_file(
        current_app.config['GOOGLE_SERVICE_ACCOUNT_FILE'],
        scopes=['https://www.googleapis.com/auth/admin.directory.group.'
                'readonly'],
        subject=current_app.config['GOOGLE_ADMIN_SUBJECT'])

    dirapi = googleapiclient.discovery.build('admin', 'directory_v1',
                                             credentials=credentials)
    groups = dirapi.groups().list(userKey=user_info['email']).execute()

    return [g['email'] for g in groups.get('groups', [])]


def handle_authorize(remote, token, user_info):
    if user_info is None:
        log_auth_failure("google", None)
        abort(401)

    if len(current_app.config['GOOGLE_ALLOWED_DOMAINS']) > 0 \
            and not user_info['hd'] in \
            current_app.config['GOOGLE_ALLOWED_DOMAINS']:
        log_auth_failure("google", user_info['sub'])
        abort(401)

    user = User(user_info)
    user_groups = get_groups(user_info)
    login_user(user, get_user_roles(user, user_groups))

    log_auth_success("google", user_info['sub'])

    return redirect_back('admin.index')
