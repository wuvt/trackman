from flask import request
from urllib.parse import urljoin


def make_external(url):
    return urljoin(request.url_root, url)


def tracklog_serialize(t):
    """Basic TrackLog serializer for deprecated API version 0."""
    return {
        'tracklog_id': t['id'],
        'track_id': t['track_id'],
        'played': t['played'],
        'djset': t['djset_id'],
        'dj_id': t['dj_id'],
        'request': t['request'],
        'vinyl': t['vinyl'],
        'new': t['new'],
        'listeners': t['listeners'],
    }


def tracklog_full_serialize(t):
    """Full TrackLog serializer for deprecated API version 0."""
    track = t['track']
    track['added'] = str(track['added'])
    return {
        'tracklog_id': t['id'],
        'track_id': t['track_id'],
        'track': track,
        'played': t['played'],
        'djset': t['djset_id'],
        'dj_id': t['dj_id'],
        'dj_visible': t['dj']['visible'],
        'dj': t['dj']['airname'],
        'request': t['request'],
        'vinyl': t['vinyl'],
        'new': t['new'],
        'rotation_id': t['rotation_id'],
        'listeners': t['listeners'],
    }
