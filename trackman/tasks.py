from . import app, auth_manager, lib
import hashlib
import hmac
import requests


def email_weekly_charts():
    with app.app_context():
        lib.email_weekly_charts()


def deduplicate_tracks():
    with app.app_context():
        lib.deduplicate_all_tracks()


def playlist_cleanup():
    with app.app_context():
        app.logger.debug("Trackman: Starting playlist cleanup...")
        lib.prune_empty_djsets()


def cleanup_dj_list_task():
    with app.app_context():
        app.logger.debug("Trackman: Starting DJ list cleanup...")
        lib.cleanup_dj_list()


def cleanup_sessions_and_claim_tokens():
    with app.app_context():
        auth_manager.cleanup_expired_sessions()
        lib.cleanup_expired_claim_tokens()


def internal_ping():
    with app.app_context():
        msg = "/internal/ping"
        sig = hmac.new(app.secret_key.encode('utf-8'),
                       msg.encode('utf-8'), hashlib.sha256)
        r = requests.get(
            app.config['TRACKMAN_API_URL'] + '/internal/ping',
            headers={'Authorization': "HMAC-SHA256 {0}".format(
                sig.hexdigest())})
        r.raise_for_status()
