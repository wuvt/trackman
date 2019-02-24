from flask import current_app
from trackman import pubsub
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

        return {
            'success': True,
        }
