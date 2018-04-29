from celery.decorators import periodic_task
from celery.task.schedules import crontab
from datetime import timedelta
from flask import json

from . import app, auth_manager, redis_conn, lib
from .celeryconfig import make_celery

celery = make_celery(app)


@periodic_task(run_every=crontab(day_of_week=1, hour=0, minute=0))
def email_weekly_charts():
    with app.app_context():
        lib.email_weekly_charts()


@periodic_task(run_every=crontab(hour=3, minute=0))
def deduplicate_tracks():
    with app.app_context():
        lib.deduplicate_all_tracks()


@periodic_task(run_every=crontab(hour=6, minute=0))
def playlist_cleanup():
    with app.app_context():
        app.logger.debug("Trackman: Starting playlist cleanup...")
        lib.prune_empty_djsets()


@periodic_task(run_every=crontab(day_of_week=1, hour=0, minute=0))
def cleanup_dj_list_task():
    with app.app_context():
        app.logger.debug("Trackman: Starting DJ list cleanup...")
        lib.cleanup_dj_list()


@periodic_task(run_every=timedelta(minutes=1))
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


@periodic_task(run_every=timedelta(seconds=55))
def publish_keepalive():
    with app.app_context():
        redis_conn.publish('trackman_live', json.dumps({
            'event': "keepalive",
        }))

        redis_conn.publish('trackman_dj_live', json.dumps({
            'event': "keepalive",
        }))


@periodic_task(run_every=crontab(hour=1, minute=0))
def cleanup_sessions_and_claim_tokens():
    with app.app_context():
        auth_manager.cleanup_expired_sessions()
        lib.cleanup_expired_claim_tokens()
