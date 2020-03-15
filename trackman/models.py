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

    def __init__(self, title, artist, album, label):
        self.title = title
        self.artist = artist
        self.album = album
        self.label = label


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
