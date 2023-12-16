import datetime
from sqlalchemy_utils import UUIDType
from . import db


class DJ(db.Model):
    __tablename__ = "dj"
    id = db.Column(db.Integer, primary_key=True)
    airname = db.Column(db.Unicode(255))
    name = db.Column(db.Unicode(255))
    phone = db.Column(db.Unicode(12))
    email = db.Column(db.Unicode(255))
    genres = db.Column(db.Unicode(255))
    time_added = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)

    def __init__(self, airname, name, visible=True):
        self.airname = airname
        self.name = name
        self.visible = visible

    def serialize(self, include_private=False, include_name=False):
        data = {
            'id': self.id,
            'airname': self.airname,
            'visible': self.visible,
        }

        if include_private:
            data.update({
                'name': self.name,
                'phone': self.phone,
                'email': self.email,
                'genres': self.genres,
                'time_added': self.time_added,
            })
        elif include_name:
            data['name'] = self.name

        return data


class DJSet(db.Model):
    __tablename__ = "set"
    # may need to make this a BigInteger
    id = db.Column(db.Integer, primary_key=True)
    dj_id = db.Column(db.Integer, db.ForeignKey('dj.id'))
    dj = db.relationship('DJ', backref=db.backref('sets', lazy='dynamic'))
    dtstart = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    dtend = db.Column(db.DateTime)

    def __init__(self, dj_id):
        self.dj_id = dj_id

    def serialize(self, include_djname=False):
        return {
            'id': self.id,
            'dj_id': self.dj_id,
            'dj': self.dj.serialize(include_name=include_djname),
            'dtstart': self.dtstart,
            'dtend': self.dtend,
        }


class DJClaim(db.Model):
    __tablename__ = "dj_claim"
    id = db.Column(db.Integer, primary_key=True)
    dj_id = db.Column(db.Integer, db.ForeignKey('dj.id'))
    dj = db.relationship('DJ', backref=db.backref('claims', lazy='dynamic'))
    sub = db.Column(db.Unicode(255), nullable=False)

    def __init__(self, dj_id, sub):
        self.dj_id = dj_id
        self.sub = sub


class DJClaimToken(db.Model):
    __tablename__ = "dj_claim_token"
    id = db.Column(db.Integer, primary_key=True)
    dj_id = db.Column(db.Integer, db.ForeignKey('dj.id'))
    dj = db.relationship('DJ', backref=db.backref('claim_tokens', lazy='dynamic'))
    sub = db.Column(db.Unicode(255), nullable=False)
    email = db.Column(db.Unicode(255))
    token = db.Column(db.Unicode(255))
    request_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, dj_id, sub, email, token):
        self.dj_id = dj_id
        self.sub = sub
        self.email = email
        self.token = token


class Rotation(db.Model):
    __tablename__ = "rotation"
    id = db.Column(db.Integer, primary_key=True)
    rotation = db.Column(db.Unicode(255))
    visible = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, rotation):
        self.rotation = rotation

    def serialize(self):
        return {
            'id': self.id,
            'rotation': self.rotation,
            'visible': self.visible,
        }


class AirLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 0 - Station ID
    # 1 - Statement of Ownership
    # 2 - PSA
    # 3 - Underwriting
    # 4 - Weather
    # 5 - Promo
    logtype = db.Column(db.Integer)
    # This is to be filled with the PSA/Promo ID
    logid = db.Column(db.Integer, nullable=True)
    airtime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    djset_id = db.Column(db.Integer, db.ForeignKey('set.id'))
    djset = db.relationship('DJSet', backref=db.backref('airlog', lazy='dynamic'))

    def __init__(self, djset_id, logtype, logid=None):
        self.djset_id = djset_id
        self.logtype = logtype
        self.logid = logid

    def serialize(self):
        return {
            'airlog_id': self.id,
            'airtime': self.airtime,
            'djset': self.djset_id,
            'logtype': self.logtype,
            'logid': self.logid,
        }


class TrackLog(db.Model):
    __tablename__ = "tracklog"
    id = db.Column(db.Integer, primary_key=True)
    # Relationships with the Track
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    track = db.relationship('Track', backref=db.backref('plays', lazy='dynamic'))
    # When the track was entered (does not count edits)
    played = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # Relationship with the playlist
    djset_id = db.Column(db.Integer, db.ForeignKey('set.id'))
    djset = db.relationship('DJSet', backref=db.backref('tracks', lazy='dynamic'))
    # DJ information, this is not kept updated right now and is _subject to removal_
    dj_id = db.Column(db.Integer, db.ForeignKey('dj.id'))
    dj = db.relationship('DJ', backref=db.backref('tracks', lazy='dynamic'))
    # Information about the track
    request = db.Column(db.Boolean, default=False)
    vinyl = db.Column(db.Boolean, default=False)
    new = db.Column(db.Boolean, default=False)
    rotation_id = db.Column(db.Integer, db.ForeignKey('rotation.id'), nullable=True)
    rotation = db.relationship('Rotation', backref=db.backref('tracks', lazy='dynamic'))
    # This should be recorded at the start of the song probably
    listeners = db.Column(db.Integer)
    title = db.Column(db.Unicode(500).with_variant(db.Unicode, 'postgresql'))
    artist = db.Column(db.Unicode(255).with_variant(db.Unicode, 'postgresql'), index=True)
    album = db.Column(db.Unicode(255).with_variant(db.Unicode, 'postgresql'))
    label = db.Column(db.Unicode(255).with_variant(db.Unicode, 'postgresql'))

    def __init__(self, track_id, djset_id, request=False, vinyl=False, new=False, rotation=None, listeners=0):
        self.track_id = track_id
        self.djset_id = djset_id

        if djset_id is not None:
            self.dj_id = DJSet.query.get(djset_id).dj_id
        else:
            # default to automation
            self.dj_id = 1

        self.request = request
        self.vinyl = vinyl
        self.new = new
        self.rotation = rotation
        self.listeners = listeners

    def serialize(self):
        return {
            'tracklog_id': self.id,
            'track_id': self.track_id,
            'played': self.played,
            'djset': self.djset_id,
            'dj_id': self.dj_id,
            'request': self.request,
            'vinyl': self.vinyl,
            'new': self.new,
            'listeners': self.listeners,
        }

    def full_serialize(self):
        return {
            'tracklog_id': self.id,
            'track_id': self.track_id,
            'track': self.track.serialize(),
            'played': self.played,
            'djset': self.djset_id,
            'dj_id': self.dj_id,
            'dj_visible': self.dj.visible,
            'dj': self.dj.airname,
            'request': self.request,
            'vinyl': self.vinyl,
            'new': self.new,
            'rotation_id': self.rotation_id,
            'listeners': self.listeners,
        }

    def api_serialize(self, include_djname=False):
        data = {
            'id': self.id,
            'track_id': self.track_id,
            'track': self.track.api_serialize(),
            'played': self.played,
            'djset_id': self.djset_id,
            'dj_id': self.dj_id,
            'dj': self.dj.serialize(include_name=include_djname),
            'request': self.request,
            'vinyl': self.vinyl,
            'new': self.new,
            'rotation_id': self.rotation_id,
            'listeners': self.listeners,
        }

        if self.rotation is not None:
            data['rotation'] = self.rotation.serialize()
        else:
            data['rotation'] = None

        if self.djset is not None:
            data['djset'] = self.djset.serialize()
        else:
            data['djset'] = None

        return data


class Track(db.Model):
    __tablename__ = "track"
    # may need to make this a BigInteger
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(500).with_variant(db.Unicode, 'postgresql'))
    artist = db.Column(db.Unicode(255).with_variant(db.Unicode, 'postgresql'), index=True)
    album = db.Column(db.Unicode(255).with_variant(db.Unicode, 'postgresql'))
    label = db.Column(db.Unicode(255).with_variant(db.Unicode, 'postgresql'))
    added = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    artist_mbid = db.Column(UUIDType())
    recording_mbid = db.Column(UUIDType())
    release_mbid = db.Column(UUIDType())
    releasegroup_mbid = db.Column(UUIDType())

    def __init__(self, title, artist, album, label, artist_mbid=None,
                 recording_mbid=None, release_mbid=None,
                 releasegroup_mbid=None):
        self.title = title
        self.artist = artist
        self.album = album
        self.label = label
        self.artist_mbid = artist_mbid
        self.recording_mbid = recording_mbid
        self.release_mbid = release_mbid
        self.releasegroup_mbid = releasegroup_mbid

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'label': self.label,
            'added': str(self.added),
            'artist_mbid': self.artist_mbid,
            'recording_mbid': self.recording_mbid,
            'release_mbid': self.release_mbid,
            'releasegroup_mbid': self.releasegroup_mbid,
        }

    def api_serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'label': self.label,
            'added': self.added,
            'artist_mbid': self.artist_mbid,
            'recording_mbid': self.recording_mbid,
            'release_mbid': self.release_mbid,
            'releasegroup_mbid': self.releasegroup_mbid,
        }


class TrackReport(db.Model):
    __tablename__ = "trackreport"
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.UnicodeText().with_variant(db.UnicodeText(length=2**1), 'mysql'))
    resolution = db.Column(db.UnicodeText().with_variant(db.UnicodeText(length=2**1), 'mysql'))
    open = db.Column(db.Boolean, default=True)
    # Track being reported
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    track = db.relationship('Track', backref=db.backref('reports', lazy='dynamic'))
    # DJ who reported the track
    dj_id = db.Column(db.Integer, db.ForeignKey('dj.id'))
    dj = db.relationship('DJ', backref=db.backref('reports', lazy='dynamic'))

    def __init__(self, dj_id, track_id, reason):
        self.track_id = track_id
        self.dj_id = dj_id
        self.reason = reason
