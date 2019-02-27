from flask import current_app
from trackman import lib, pubsub, redis_conn
from trackman.view_utils import check_request_sig
from .base import TrackmanResource


class InternalResource(TrackmanResource):
    method_decorators = [check_request_sig]


class InternalPing(InternalResource):
    def get(self):
        """
        Internal ping used to trigger events such as keepalives.
        This should be triggered approximately once per minute.
        ---
        operationId: internalPing
        tags:
        - trackman
        """
        pubsub.publish(
            current_app.config['PUBSUB_PUB_URL_ALL'],
            message={'event': "keepalive"})
        pubsub.publish(
            current_app.config['PUBSUB_PUB_URL_DJ'],
            message={'event': "keepalive"})

        dj_active = redis_conn.get('dj_active')
        automation = redis_conn.get('automation_enabled')
        # dj_active is None if dj_active has expired (no activity)
        if dj_active is None:
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

        return {
            'success': True,
        }
