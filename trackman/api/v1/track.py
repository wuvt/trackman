from flasgger import swag_from
from flask import request, session
from flask_restful import abort
from trackman import db, models, ma
from trackman.forms import TrackAddForm
from trackman.lib import find_or_add_track
from .base import TrackmanResource, TrackmanDJResource
from .schemas import TrackSchema


class TrackResponseSchema(ma.Schema):
    success = ma.Boolean()
    track = ma.Nested(TrackSchema)


class Track(TrackmanDJResource):
    @swag_from({
        'operationId': "getTrackById",
        'tags': ['private', 'track'],
        'parameters': [
            {
                'in': "path",
                'name': "track_id",
                'type': "integer",
                'required': True,
                'description': "The ID of an existing track",
            },
        ],
        'responses': {
            200: {
                'schema': TrackResponseSchema,
            },
            404: {
                'description': "Track not found",
            },
        },
    })
    def get(self, track_id):
        """Get information about a track."""
        track = models.Track.query.get(track_id)
        if not track:
            abort(404, success=False, message="Track not found")

        schema =  TrackResponseSchema()
        return schema.dump({
            'success': True,
            'track': track,
        })


class TrackReport(TrackmanResource):
    @swag_from({
        'operationId': "reportTrack",
        'tags': ['private', 'track'],
        'parameters': [
            {
                'in': "path",
                'name': "track_id",
                'type': "integer",
                'required': True,
                'description': "The ID of an existing track",
            },
            {
                'in': "form",
                'name': "reason",
                'type': "string",
                'required': True,
                'description': "The reason for reporting the track",
            },
            {
                'in': "form",
                'name': "dj_id",
                'type': "integer",
                'required': True,
                'description': "The DJ to associate with the report",
            },
        ],
        'responses': {
            201: {
                'description': "Track report created",
            },
            404: {
                'description': "Track not found",
            },
        },
    })
    def post(self, track_id):
        """Report a metadata issue with a track."""
        track = models.Track.query.get(track_id)
        if not track:
            abort(404, success=False, message="Track not found")

        reason = request.form['reason'].strip()
        if len(reason) <= 0:
            abort(400, success=False, message="A reason must be provided")

        dj_id = session['dj_id']

        report = models.TrackReport(dj_id, track_id, reason)
        db.session.add(report)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return {
            'success': True,
        }


class TrackSearchResponseSchema(ma.Schema):
    success = ma.Boolean()
    message = ma.String()
    results = ma.Nested(TrackSchema, many=True)


class TrackSearch(TrackmanResource):
    @swag_from({
        'operationId': "searchTracks",
        'tags': ['private', 'track'],
        'parameters': [
            {
                'in': "form",
                'name': "artist",
                'type': "string",
                'description': "Partial artist name",
            },
            {
                'in': "form",
                'name': "title",
                'type': "string",
                'description': "Partial track title",
            },
            {
                'in': "form",
                'name': "album",
                'type': "string",
                'description': "Partial album title",
            },
            {
                'in': "form",
                'name': "label",
                'type': "string",
                'description': "Partial record label",
            },
        ],
        'responses': {
            200: {
                'description': "Search results",
                'schema': TrackSearchResponseSchema,
            },
            400: {
                'description': "Bad request",
            },
        },
    })
    def get(self):
        """Search the track database for a particular track."""
        base_query = models.Track.query.outerjoin(models.TrackLog).\
            order_by(models.Track.plays)
        schema = TrackSearchResponseSchema()

        # To verify some data was searched for
        somesearch = False

        tracks = base_query

        # Do case-insensitive exact matching first

        artist = request.args.get('artist', '').strip()
        if len(artist) > 0:
            somesearch = True
            tracks = tracks.filter(
                db.func.lower(models.Track.artist) == db.func.lower(artist))

        title = request.args.get('title', '').strip()
        if len(title) > 0:
            somesearch = True
            tracks = tracks.filter(
                db.func.lower(models.Track.title) == db.func.lower(title))

        album = request.args.get('album', '').strip()
        if len(album) > 0:
            somesearch = True
            tracks = tracks.filter(
                db.func.lower(models.Track.album) == db.func.lower(album))

        label = request.args.get('label', '').strip()
        if len(label) > 0:
            somesearch = True
            tracks = tracks.filter(
                db.func.lower(models.Track.label) == db.func.lower(label))

        # This means there was a bad search, stop searching
        if somesearch is False:
            return schema.dump({
                'success': False,
                'message': "All provided fields to match against are empty",
                'results': [],
            })

        # Check if results

        tracks = tracks.limit(8).all()
        if len(tracks) == 0:
            tracks = base_query

            # if there are too few results, append some similar results
            artist = request.args.get('artist', '').strip()
            if len(artist) > 0:
                somesearch = True
                tracks = tracks.filter(
                    models.Track.artist.ilike(''.join(['%', artist, '%'])))

            title = request.args.get('title', '').strip()
            if len(title) > 0:
                somesearch = True
                tracks = tracks.filter(
                    models.Track.title.ilike(''.join(['%', title, '%'])))

            album = request.args.get('album', '').strip()
            if len(album) > 0:
                somesearch = True
                tracks = tracks.filter(
                    models.Track.album.ilike(''.join(['%', album, '%'])))

            label = request.args.get('label', '').strip()
            if len(label) > 0:
                somesearch = True
                tracks = tracks.filter(
                    models.Track.label.ilike(''.join(['%', label, '%'])))

            tracks = tracks.limit(8).all()

        return schema.dump({
            'success': True,
            'results': tracks,
        })


class TrackAutoComplete(TrackmanResource):
    @swag_from({
        'operationId': "autocompleteTracks",
        'tags': ['private', 'track'],
        'parameters': [
            {
                'in': "query",
                'name': "artist",
                'type': "string",
                'description': "Partial artist name",
            },
            {
                'in': "query",
                'name': "title",
                'type': "string",
                'description': "Partial track title",
            },
            {
                'in': "query",
                'name': "album",
                'type': "string",
                'description': "Partial album title",
            },
            {
                'in': "query",
                'name': "label",
                'type': "string",
                'description': "Partial record label",
            },
        ],
        'responses': {
            200: {
                'description': "Search results",
                'schema': TrackSearchResponseSchema,
            },
            400: {
                'description': "Bad request",
            },
        },
    })

    def get(self):
        """Search the track database for a particular field."""
        schema = TrackSearchResponseSchema()
        field = request.args['field']
        if field == 'artist':
            base_query = models.Track.query.\
                with_entities(models.Track.artist).\
                group_by(models.Track.artist)
        elif field == 'title':
            base_query = models.Track.query.\
                with_entities(models.Track.title).\
                group_by(models.Track.title)
        elif field == 'album':
            base_query = models.Track.query.\
                with_entities(models.Track.album).\
                group_by(models.Track.album)
        elif field == 'label':
            base_query = models.Track.query.\
                with_entities(models.Track.label).\
                group_by(models.Track.label)
        else:
            return schema.dump({
                'success': False,
                'message': "Unknown field provided to use for autocomplete",
                'results': [],
            })

        # To verify some data was searched for
        somesearch = False

        tracks = base_query

        artist = request.args.get('artist', '').strip()
        if len(artist) > 0:
            somesearch = True
            tracks = tracks.filter(
                models.Track.artist.ilike('{0}%'.format(artist)))

        title = request.args.get('title', '').strip()
        if len(title) > 0:
            somesearch = True
            tracks = tracks.filter(
                models.Track.title.ilike('{0}%'.format(title)))

        album = request.args.get('album', '').strip()
        if len(album) > 0:
            somesearch = True
            tracks = tracks.filter(
                models.Track.album.ilike('{0}%'.format(album)))

        label = request.args.get('label', '').strip()
        if len(label) > 0:
            somesearch = True
            tracks = tracks.filter(
                models.Track.label.ilike('{0}%'.format(label)))

        # This means there was a bad search, stop searching
        if somesearch is False:
            return schema.dump({
                'success': False,
                'message': "All provided fields to match against are empty",
                'results': [],
            })

        # Check if results

        tracks = tracks.limit(25).all()
        if len(tracks) > 0:
            results = [t[0] for t in tracks]
        else:
            results = []

        return schema.dump({
            'success': True,
            'results': results,
        })


class TrackCreateResponseSchema(ma.Schema):
    success = ma.Boolean()
    track_id = ma.Integer()


class TrackList(TrackmanResource):
    @swag_from({
        'operationId': "createTrack",
        'tags': ['private', 'track'],
        'parameters': [
            {
                'in': "form",
                'name': "artist",
                'type': "string",
                'required': True,
                'description': "Artist name",
            },
            {
                'in': "form",
                'name': "title",
                'type': "string",
                'required': True,
                'description': "Track title",
            },
            {
                'in': "form",
                'name': "album",
                'type': "string",
                'required': True,
                'description': "Album title",
            },
            {
                'in': "form",
                'name': "label",
                'type': "string",
                'required': True,
                'description': "Record label",
            },
        ],
        'responses': {
            201: {
                'description': "Track created",
                'schema': TrackCreateResponseSchema,
            },
            400: {
                'description': "Bad request",
            },
        },
    })
    def post(self):
        """Create a new track in the database."""
        form = TrackAddForm(meta={'csrf': False})
        if form.validate():
            track = find_or_add_track(models.Track(
                form.title.data,
                form.artist.data,
                form.album.data,
                form.label.data))

            schema = TrackCreateResponseSchema()
            return schema.dump({
                'success': True,
                'track_id': track.id,
            }), 201
        else:
            abort(400, success=False, errors=form.errors,
                  message="The track information you entered did not validate. Common reasons for this include missing or improperly entered information, especially the label. Please try again. If you continue to get this message after several attempts, and you're sure the information is correct, please contact the IT staff for help.")
