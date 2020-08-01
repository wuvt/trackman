#!/usr/bin/python3

import argparse
import mutagen
import requests

parser = argparse.ArgumentParser(
    description="Submit a playlist of tracks to Trackman")
parser.add_argument('playlist', help="A text file with one file per line")
args = parser.parse_args()

musicbrainz_fields = {
    "artist_mbid": "musicbrainz_artistid",
    "recording_mbid": "musicbrainz_trackid",
    "release_mbid": "musicbrainz_albumid",
    "releasegroup_mbid": "musicbrainz_releasegroupid",
}

with open(args.playlist) as f:
    for line in f:
        path = line.strip()
        track = mutagen.File(path)
        data = {
            'password': "hackme",
            'title': track.get('title', ''),
            'artist': track.get('artist', ''),
            'album': track.get('album', ''),
            'label': track.get('label', ''),
        }

        for data_key, metadata_key in musicbrainz_fields.items():
            value = track.get(metadata_key)
            if value is not None and len(value) > 0:
                data[data_key] = value[0]

        r = requests.post(
            'http://localhost:9070/api/automation/log',
            data=data)
        r.raise_for_status()
