from dateutil import tz
from flask import current_app
from marshmallow.decorators import pre_dump, post_dump
from marshmallow.utils import get_value
from trackman import ma, models


class DJSchema(ma.SQLAlchemySchema):
    class Meta:
        model = models.DJ

    id = ma.auto_field()
    airname = ma.auto_field()
    visible = ma.auto_field()


class DJPrivateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.DJ


class DJSetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.DJSet
        include_fk = True

    dj = ma.Nested(DJSchema)

    @pre_dump
    def set_timezone(self, djset, **kwargs):
        if djset.dtstart is not None and djset.dtstart.tzinfo is None:
            djset.dtstart = djset.dtstart.replace(tzinfo=tz.tzutc())
        if djset.dtend is not None and djset.dtend.tzinfo is None:
            djset.dtend = djset.dtend.replace(tzinfo=tz.tzutc())
        return djset


class RotationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Rotation


class AirLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.AirLog
        include_fk = True

    dj = ma.Nested(DJSchema)
    djset = ma.Nested(DJSetSchema)

    @pre_dump
    def set_timezone(self, airlog, **kwargs):
        if airlog.airtime.tzinfo is None:
            airlog.airtime = airlog.airtime.replace(tzinfo=tz.tzutc())
        return airlog


class TrackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Track

    plays = ma.List(ma.Nested(lambda: TrackLogSchema(exclude=('track',))))

    @pre_dump
    def set_timezone(self, track, **kwargs):
        if track.added.tzinfo is None:
            track.added = track.added.replace(tzinfo=tz.tzutc())
        return track


class TrackLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.TrackLog
        include_fk = True
        exclude = ('album', 'artist', 'title', 'label')

    dj = ma.Nested(DJSchema)
    djset = ma.Nested(DJSetSchema)
    track = ma.Nested(lambda: TrackSchema(exclude=('plays',)))
    rotation = ma.Nested(RotationSchema)

    @pre_dump
    def set_timezone(self, tracklog, **kwargs):
        if tracklog.played.tzinfo is None:
            tracklog.played = tracklog.played.replace(tzinfo=tz.tzutc())
        return tracklog


class TrackLogModifiedSchema(ma.SQLAlchemyAutoSchema):
    """TrackLogModifiedSchema is very similar to the standard TrackLogSchema,
    but with a few minor changes. DJ data is flatted into dj_id, dj, and
    dj_visible fields with contain the DJ ID, DJ Airname, and DJ Visible
    fields, respectively. The "djset" field contains only the DJSet ID. The
    "id" field is also renamed to "tracklog_id."

    This functionality is used by the Trackman logging interface and in SSE
    messages."""

    class Meta:
        model = models.TrackLog
        include_fk = True
        exclude = ('album', 'artist', 'title', 'label', 'dj', 'djset')

    dj = ma.String()
    djset = ma.Integer()
    track = ma.Nested(lambda: TrackSchema(exclude=('plays',)))

    @pre_dump
    def set_timezone(self, tracklog, **kwargs):
        if tracklog.played.tzinfo is None:
            tracklog.played = tracklog.played.replace(tzinfo=tz.tzutc())
        return tracklog

    @post_dump(pass_original=True)
    def set_dj(self, item, tracklog, **kwargs):
        item['dj'] = tracklog.dj.airname
        item['dj_visible'] = tracklog.dj.visible
        return item

    @post_dump
    def rename_djset(self, item, **kwargs):
        item['djset'] = item.pop('djset_id')
        return item

    @post_dump
    def rename_tracklog_id(self, item, **kwargs):
        item['tracklog_id'] = item.pop('id')
        return item


class TrackLogLegacySchema(ma.Schema):
    class Meta:
        model = models.Track

    id = ma.Integer()
    dj = ma.String()
    dj_id = ma.Integer()
    listeners = ma.Integer()
    played = ma.DateTime()
    title = ma.String()
    artist = ma.String()
    album = ma.String()
    label = ma.String()
    added = ma.DateTime()
    artist_mbid = ma.UUID()
    recording_mbid = ma.UUID()
    release_mbid = ma.UUID()
    releasegroup_mbid = ma.UUID()
    contact = ma.String()
    description = ma.String()

    def get_attribute(self, obj, attr, default):
        # Most attributes come from the track itself
        if attr in ('dj_id', 'listeners', 'played'):
            # get value from object directly
            return get_value(obj, attr, default)
        elif attr == 'dj':
            # get DJ airname
            return get_value(obj.dj, 'airname', default)
        else:
            # get value from track property of object
            return get_value(obj.track, attr, default)

    @pre_dump
    def set_dj_info(self, tracklog, many, **kwargs):
        if tracklog is None:
            dj = models.DJ.query.get(1)
            tracklog.dj = dj
            tracklog.dj_id = 0
        elif not tracklog.djset.dj.visible:
            tracklog.dj_id = 0

        return tracklog

    @pre_dump
    def set_timezone(self, tracklog, **kwargs):
        if tracklog.played.tzinfo is None:
            tracklog.played = tracklog.played.replace(tzinfo=tz.tzutc())
        if tracklog.track.added.tzinfo is None:
            tracklog.track.added = tracklog.track.added.replace(
                tzinfo=tz.tzutc())
        return tracklog

    @post_dump
    def set_contact_and_description(self, item, many, **kwargs):
        item['contact'] = current_app.config['STATION_URL']
        item['description'] = current_app.config['STATION_NAME']
        return item


class TrackReportSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.TrackReport
        include_fk = True
