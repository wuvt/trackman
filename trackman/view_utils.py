from flask import abort, current_app, request, session, url_for  # noqa: F401
from flask_restful import abort as restful_abort
from functools import wraps
import hashlib
import hmac
import netaddr
import re
import unidecode
from datetime import timedelta
from urllib.parse import urljoin
from . import app, auth_manager
from .auth.utils import current_user, current_user_roles
from .lib import perdelta, renew_dj_lease, check_onair


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
_slug_pattern = re.compile(r"[^ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._~:/?#\[\]@!$&'()*+,;=\-]*")


class IPAccessDeniedException(Exception):
    pass


def local_only(f):
    @wraps(f)
    def local_wrapper(*args, **kwargs):
        if request.remote_addr not in \
                netaddr.IPSet(app.config['INTERNAL_IPS']):
            raise IPAccessDeniedException()
        else:
            return f(*args, **kwargs)
    return local_wrapper


def dj_only(f):
    auth_manager.all_roles.update(set(['dj']))
    internal_ipset = netaddr.IPSet(app.config['INTERNAL_IPS'])

    @wraps(f)
    def local_wrapper(*args, **kwargs):
        if (current_user.is_authenticated and 'dj' in current_user_roles) or \
                request.remote_addr in internal_ipset:
            return f(*args, **kwargs)
        elif not current_user.is_authenticated:
            return auth_manager.unauthorized()
        else:
            abort(403)
    return local_wrapper


def ajax_only(f):
    """This decorator verifies that the X-Requested-With header is present.
    JQuery adds this header, and we can use it to prevent cross-origin requests
    because it cannot be added without a CORS preflight check."""

    @wraps(f)
    def ajax_only_wrapper(*args, **kwargs):
        if request.headers.get('X-Requested-With', '') != "":
            return f(*args, **kwargs)
        else:
            return abort(403)
    return ajax_only_wrapper


def slugify(text, delim='-'):
    """Generates an ASCII-only slug and validates that it is an acceptable
    character set as per rfc3986"""
    if _slug_pattern.match(text) is None:
        return False

    # from http://flask.pocoo.org/snippets/5/
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode.unidecode(word).split())
    return str(delim.join(result))


def dj_interact(f):
    @wraps(f)
    def dj_wrapper(*args, **kwargs):
        # Call in the function first in case it changes the timeout
        ret = f(*args, **kwargs)

        if check_onair(session.get('djset_id', None)):
            renew_dj_lease()

        return ret
    return dj_wrapper


def make_external(url):
    return urljoin(request.url_root, url)


def list_archives(djset):
    if len(current_app.config['ARCHIVE_URL_FORMAT']) <= 0:
        return

    start = djset.dtstart.replace(minute=0, second=0, microsecond=0)

    if djset.dtend is None:
        end = start
    else:
        end = djset.dtend.replace(minute=0, second=0, microsecond=0)

    for loghour in perdelta(start, end, timedelta(hours=1)):
        yield (loghour.strftime(current_app.config['ARCHIVE_URL_FORMAT']),
               loghour,
               loghour + timedelta(hours=1))


def require_dj_session(f):
    @wraps(f)
    def require_dj_session_wrapper(*args, **kwargs):
        if session.get('dj_id', None) is None:
            restful_abort(
                403,
                message="You must login as a DJ to use that feature.")
        else:
            return f(*args, **kwargs)
    return require_dj_session_wrapper


def require_onair(f):
    @wraps(f)
    def require_onair_wrapper(*args, **kwargs):
        if not check_onair(session.get('djset_id', None)):
            restful_abort(
                403,
                message="You must be on-air to use that feature.",
                onair=False)
        else:
            return f(*args, **kwargs)
    return require_onair_wrapper


def check_request_sig(f):
    @wraps(f)
    def check_request_sig_wrapper(*args, **kwargs):
        expected = hmac.new(current_app.secret_key.encode('utf-8'),
                            request.path.replace('/api', '').encode('utf-8'),
                            hashlib.sha256).hexdigest()
        auth = request.headers.get('Authorization')

        if auth is not None:
            auth_split = auth.split(' ', 1)
            if len(auth_split) > 1 and auth_split[0] == 'HMAC-SHA256' and \
                    hmac.compare_digest(expected, auth_split[1]):
                return f(*args, **kwargs)
            else:
                restful_abort(
                    401,
                    message="Bad request signature.")
        else:
            restful_abort(
                401,
                message="Bad request signature.")
    return check_request_sig_wrapper


def can_view_dj_private_info():
    return current_user.is_authenticated and (
        'admin' in current_user_roles or 'library' in current_user_roles)
