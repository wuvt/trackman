from flasgger import swag_from
from flask_restful import abort, Resource
from trackman import db, charts, ma
from trackman.models import DJ, Track, TrackLog
from .base import ChartResource
from .schemas import DJSchema, TrackSchema


class Charts(Resource):
    @swag_from({
        'operationId': "getChartTypes",
        'tags': ['public', 'charts'],
    })
    def get(self):
        """Get a list of chart types."""
        return {
            'albums': "Top albums",
            'artists': "Top artists",
            'tracks': "Top tracks",
        }


class AlbumChartsSchema(ma.Schema):
    start = ma.DateTime()
    end = ma.DateTime()
    results = ma.List(ma.Tuple((ma.String, ma.String, ma.String, ma.String)))


class AlbumCharts(ChartResource):
    @swag_from({
        'operationId': "getAlbumCharts",
        'tags': ['public', 'charts'],
        'responses': {
            200: {
                'schema': AlbumChartsSchema,
            },
        },
    })
    def get(self, period=None, year=None, month=None):
        """Get album charts."""
        try:
            start, end = charts.get_range(period, year, month)
        except ValueError:
            abort(404)

        results = charts.get(
            'albums_{0}_{1}'.format(start, end),
            Track.query.with_entities(
                db.func.min(Track.artist),
                db.func.min(Track.album),
                db.func.count(TrackLog.id)).
            join(TrackLog).filter(db.and_(
                TrackLog.dj_id > 1,
                TrackLog.played >= start,
                TrackLog.played <= end)).
            group_by(db.func.lower(Track.artist),
                     db.func.lower(Track.album)).
            order_by(db.func.count(TrackLog.id).desc()))

        schema = AlbumChartsSchema()
        return schema.dump({
            'start': start,
            'end': end,
            'results': [(x[0], x[1], x[2], x[3]) for x in results],
        })


class DJAlbumChartsSchema(ma.Schema):
    dj = ma.Nested(DJSchema)
    results = ma.List(ma.Tuple((ma.String, ma.String, ma.String, ma.String)))


class DJAlbumCharts(ChartResource):
    @swag_from({
        'operationId': "getDJAlbumCharts",
        'tags': ['public', 'charts'],
        'responses': {
            200: {
                'schema': DJAlbumChartsSchema,
            },
        },
    })
    def get(self, dj_id):
        """Get album charts by DJ."""
        dj = DJ.query.get_or_404(dj_id)
        results = charts.get(
            'albums_dj_{}'.format(dj_id),
            Track.query.with_entities(
                db.func.min(Track.artist),
                db.func.min(Track.album),
                db.func.count(TrackLog.id)).
            join(TrackLog).filter(TrackLog.dj_id == dj.id).
            group_by(db.func.lower(Track.artist),
                     db.func.lower(Track.album)).
            order_by(db.func.count(TrackLog.id).desc()))

        chema = DJAlbumChartsSchema()
        return schema.dump({
            'dj': dj,
            'results': [(x[0], x[1], x[2], x[3]) for x in results],
        })


class ArtistChartsSchema(ma.Schema):
    start = ma.DateTime()
    end = ma.DateTime()
    results = ma.List(ma.Tuple((ma.String, ma.String, ma.String)))


class ArtistCharts(ChartResource):
    @swag_from({
        'operationId': "getArtistCharts",
        'tags': ['public', 'charts'],
        'responses': {
            200: {
                'schema': ArtistChartsSchema,
            },
        },
    })
    def get(self, period=None, year=None, month=None):
        """Get artist charts."""
        try:
            start, end = charts.get_range(period, year, month)
        except ValueError:
            abort(404)

        results = charts.get(
            'artists_{0}_{1}'.format(start, end),
            Track.query.with_entities(
                db.func.min(Track.artist),
                db.func.count(TrackLog.id)).
            join(TrackLog).filter(db.and_(
                TrackLog.dj_id > 1,
                TrackLog.played >= start,
                TrackLog.played <= end)).
            group_by(db.func.lower(Track.artist)).
            order_by(db.func.count(TrackLog.id).desc()))

        schema = ArtistChartsSchema()
        return schema.dump({
            'start': start,
            'end': end,
            'results': [(x[0], x[1], x[2]) for x in results],
        })


class DJArtistChartsSchema(ma.Schema):
    dj = ma.Nested(DJSchema)
    results = ma.List(ma.Tuple((ma.String, ma.String, ma.String)))


class DJArtistCharts(ChartResource):
    @swag_from({
        'operationId': "getDJArtistCharts",
        'tags': ['public', 'charts'],
        'responses': {
            200: {
                'schema': DJArtistChartsSchema,
            },
        },
    })
    def get(self, dj_id):
        """Get artist charts by DJ."""
        dj = DJ.query.get_or_404(dj_id)
        results = charts.get(
            'artists_dj_{}'.format(dj_id),
            Track.query.with_entities(
                db.func.min(Track.artist),
                db.func.count(TrackLog.id)).
            join(TrackLog).filter(TrackLog.dj_id == dj.id).
            group_by(db.func.lower(Track.artist)).
            order_by(db.func.count(TrackLog.id).desc()))

        schema = DJArtistChartsSchema()
        return schema.dump({
            'dj': dj,
            'results': [(x[0], x[1], x[2]) for x in results],
        })


class TrackChartsSchema(ma.Schema):
    start = ma.DateTime()
    end = ma.DateTime()
    results = ma.List(ma.Tuple((ma.Nested(TrackSchema), ma.String, ma.String)))


class TrackCharts(ChartResource):
    @swag_from({
        'operationId': "getTrackCharts",
        'tags': ['public', 'charts'],
        'responses': {
            200: {
                'schema': TrackChartsSchema,
            },
        },
    })
    def get(self, period=None, year=None, month=None):
        """Get track charts."""
        try:
            start, end = charts.get_range(period, year, month)
        except ValueError:
            abort(404)

        subquery = TrackLog.query.\
            with_entities(TrackLog.track_id,
                          db.func.count(TrackLog.id).label('count')).\
            filter(TrackLog.dj_id > 1,
                   TrackLog.played >= start,
                   TrackLog.played <= end).\
            group_by(TrackLog.track_id).subquery()
        results = charts.get(
            'tracks_{start}_{end}'.format(start=start, end=end),
            Track.query.with_entities(Track, subquery.c.count).
            join(subquery).order_by(db.desc(subquery.c.count)))

        schema = TrackChartsSchema()
        return schema.dump({
            'start': start,
            'end': end,
            'results': [(x[0], x[1], x[2]) for x in results],
        })


class DJTrackChartsSchema(ma.Schema):
    dj = ma.Nested(DJSchema)
    results = ma.List(ma.Tuple((ma.Nested(TrackSchema), ma.String, ma.String)))


class DJTrackCharts(ChartResource):
    @swag_from({
        'operationId': "getDJTrackCharts",
        'tags': ['public', 'charts'],
        'responses': {
            200: {
                'schema': DJTrackChartsSchema,
            },
        },
    })
    def get(self, dj_id):
        """Get track charts by DJ."""
        dj = DJ.query.get_or_404(dj_id)

        subquery = TrackLog.query.\
            with_entities(TrackLog.track_id,
                          db.func.count(TrackLog.id).label('count')).\
            filter(TrackLog.dj_id == dj.id).\
            group_by(TrackLog.track_id).subquery()
        results = charts.get(
            'tracks_dj_{}'.format(dj_id),
            Track.query.with_entities(Track, subquery.c.count).
            join(subquery).order_by(db.desc(subquery.c.count)))

        schema = DJTrackChartsSchema()
        return schema.dump({
            'dj': dj,
            'results': [
                (x[0], x[1], x[2]) for x in results
            ],
        })


class DJSpinChartsSchema(ma.Schema):
    results = ma.List(ma.Tuple((ma.Nested(DJSchema), ma.String, ma.String)))


class DJSpinCharts(ChartResource):
    @swag_from({
        'operationId': "getDJSpinCharts",
        'tags': ['public', 'charts'],
        'responses': {
            200: {
                'schema': DJSpinChartsSchema,
            },
        },
    })
    def get(self):
        """Get DJs sorted by number of spins."""
        subquery = TrackLog.query.\
            with_entities(TrackLog.dj_id,
                          db.func.count(TrackLog.id).label('count')).\
            group_by(TrackLog.dj_id).subquery()

        results = charts.get(
            'dj_spins',
            DJ.query.with_entities(DJ, subquery.c.count).
            join(subquery).filter(DJ.visible == True).
            order_by(db.desc(subquery.c.count)))

        schema = DJSpinChartsSchema()
        return schema.dump({
            'results': [(x[0], x[1], x[2]) for x in results],
        })


class DJVinylSpinCharts(ChartResource):
    @swag_from({
        'operationId': "getDJVinylSpinCharts",
        'tags': ['public', 'charts'],
        'responses': {
            200: {
                'schema': DJSpinChartsSchema,
            },
        },
    })
    def get(self):
        """Get DJs sorted by number of vinyl spins."""
        subquery = TrackLog.query.\
            with_entities(TrackLog.dj_id,
                          db.func.count(TrackLog.id).label('count')).\
            filter(TrackLog.vinyl == True).\
            group_by(TrackLog.dj_id).subquery()

        results = charts.get(
            'dj_vinyl_spins',
            DJ.query.with_entities(DJ, subquery.c.count).
            join(subquery).filter(DJ.visible == True).
            order_by(db.desc(subquery.c.count)))

        schema = DJSpinChartsSchema()
        return {
            'results': [(x[0], x[1], x[2]) for x in results],
        }
