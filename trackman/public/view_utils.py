from flask import request
from urllib.parse import urljoin


def make_external(url):
    return urljoin(request.url_root, url)
