import googleapiclient.discovery
import requests
from authlib.jose import jwt, jwk
from flask import abort, current_app
from google.oauth2 import service_account
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

    user_groups = get_groups(user_info)
    login_user(user_info, get_user_roles(user, user_groups))

    log_auth_success("google", user_info['sub'])

    return redirect_back('admin.index')


def validate_security_token(token):
    # Get Google's RISC configuration.
    risc_config_uri = 'https://accounts.google.com/.well-known/risc-configuration'
    risc_config = requests.get(risc_config_uri).json()

    def load_key(header, payload):
        google_certs = requests.get(risc_config['jwks_uri']).json()
        return jwk.loads(google_certs, header.get('kid'))

    claims_options = {
        'iss': {
            'values': [risc_config['issuer']],
        },
    }
    claim_params = {
        'client_id': current_app.config['GOOGLE_CLIENT_ID'],
    }

    claims = jwt.decode(token['id_token'],
                        key=load_key,
                        claims_options=claims_options,
                        claims_params=claims_params)
    claims.validate_iss()
    claims.validate_aud()
    claims.validate_jti()
    return claims


def handle_security_event(token):
    risc_prefix = 'https://schemas.openid.net/secevent/risc/event-type'
    claims = validate_security_token(token)

    for event in claims['events'][risc_prefix + '/sessions-revoked']:
        current_app.logger.info("RISC: Sessions revoked for user {0}".format(
            event['subject']['sub']))
        current_app.auth_manager.end_all_sessions_for_user(
            event['subject']['sub'])

    for event in claims['events'][risc_prefix + '/tokens-revoked']:
        current_app.logger.info("RISC: Tokens revoked for user {0}".format(
            event['subject']['sub']))
        current_app.auth_manager.end_all_sessions_for_user(
            event['subject']['sub'])

    for event in claims['events'][risc_prefix + '/account-disabled']:
        if event['reason'] == 'hijacking':
            current_app.logger.info(
                "RISC: Disabled user {0} due to hijacking".format(
                    event['subject']['sub']))
            current_app.auth_manager.end_all_sessions_for_user(
                event['subject']['sub'])

    for event in claims['events'][risc_prefix + '/verification']:
        current_app.logger.info("Test RISC token received")
