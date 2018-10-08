from flask import json
import requests


def publish(url, message):
    r = requests.post(
        url,
        data=json.dumps(message),
        headers={'Accept': "application/json"})
    r.raise_for_status()
    return r.json()
