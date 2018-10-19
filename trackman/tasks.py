from . import app, auth_manager, redis_conn, lib


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


def autologout_check():
    with app.app_context():
        active = redis_conn.get('dj_active')
        automation = redis_conn.get('automation_enabled')
        # active is None if dj_active has expired (no activity)
        if active is None:
            if automation is None:
                # This happens when the key is missing;
                # We just bail out because we don't know the current state
                pass
            elif automation == b"true":
                # Automation is already enabled, carry on
                pass
            else:
                # Automation is disabled; end djset if exists and start
                # automation
                lib.logout_all(send_email=True)
                lib.enable_automation()


def cleanup_sessions_and_claim_tokens():
    with app.app_context():
        auth_manager.cleanup_expired_sessions()
        lib.cleanup_expired_claim_tokens()
