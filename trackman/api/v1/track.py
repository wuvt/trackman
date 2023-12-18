from flask import request, session, current_app
from flask_restful import abort
from thefuzz import fuzz, process
from trackman import db, models
from trackman.forms import TrackAddForm
from trackman.lib import find_or_add_track
from trackman.musicbrainz import musicbrainzngs
from .base import TrackmanResource, TrackmanDJResource


class Track(TrackmanDJResource):
    def get(self, track_id):
        """
        Get information about a Track
        ---
        operationId: getTrackById
        tags:
        - trackman
        - djset
        parameters:
        - in: path
          name: track_id
          type: integer
          required: true
          description: The ID of an existing Track
        responses:
          404:
            description: Track not found
        """
        track = models.Track.query.get(track_id)
        if not track:
            abort(404, success=False, message="Track not found")

        return {
            'success': True,
            'track': track.serialize(),
        }


class TrackReport(TrackmanResource):
    def post(self, track_id):
        """
        Report a Track
        ---
        operationId: getTrackById
        tags:
        - trackman
        - djset
        parameters:
        - in: path
          name: track_id
          type: integer
          required: true
          description: The ID of an existing Track
        - in: form
          name: reason
          type: string
          required: true
          description: The reason for reporting the track
        - in: form
          name: dj_id
          type: integer
          required: true
          description: The DJ to associate with the report
        responses:
          201:
            description: Track report created
          404:
            description: Track not found
        """
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


class TrackSearch(TrackmanResource):
    def get(self):
        """
        Search the track database for a particular track
        ---
        operationId: searchTracks
        tags:
        - trackman
        - track
        definitions:
        - schema:
            id: Track
            properties:
              id:
                type: integer
                description: The ID of the track
              title:
                type: string
                description: Track title
              artist:
                type: string
                description: Artist name
              album:
                type: string
                description: Album name
              label:
                type: string
                description: Record label
              added:
                type: string
                description: Date added
        parameters:
        - in: query
          name: artist
          type: string
          description: Partial artist name
        - in: query
          name: title
          type: string
          description: Partial track title
        - in: query
          name: album
          type: string
          description: Partial album title
        - in: query
          name: label
          type: string
          description: Partial record label
        responses:
          200:
            description: Search results
            schema:
              type: object
              properties:
                success:
                  type: boolean
                results:
                  type: array
                  $ref: '#/definitions/Track'
          400:
            description: Bad request
        """

        musicbrainzngs.set_hostname(current_app.config['MUSICBRAINZ_HOSTNAME'])
        musicbrainzngs.set_rate_limit(current_app.config['MUSICBRAINZ_RATE_LIMIT'])
        musicbrainz_search = {}

        base_query = models.Track.query.outerjoin(models.TrackLog).\
            order_by(models.Track.plays)

        # To verify some data was searched for
        somesearch = False

        tracks = base_query

        # Do case-insensitive exact matching first

        artist = request.args.get('artist', '').strip()
        if len(artist) > 0:
            somesearch = True
            tracks = tracks.filter(
                db.func.lower(models.Track.artist) == db.func.lower(artist))
            musicbrainz_search['artist'] = artist

        title = request.args.get('title', '').strip()
        if len(title) > 0:
            somesearch = True
            tracks = tracks.filter(
                db.func.lower(models.Track.title) == db.func.lower(title))
            musicbrainz_search['recording'] = title

        album = request.args.get('album', '').strip()
        if len(album) > 0:
            somesearch = True
            tracks = tracks.filter(
                db.func.lower(models.Track.album) == db.func.lower(album))
            musicbrainz_search['release'] = album

        # FIXME: disabled since MusicBrainz cannot search by label
        #label = request.args.get('label', '').strip()
        #if len(label) > 0:
        #    somesearch = True
        #    tracks = tracks.filter(
        #        db.func.lower(models.Track.label) == db.func.lower(label))

        # This means there was a bad search, stop searching
        # FIXME: MusicBrainz cannot search by label
        if somesearch is False:
            return {
                'success': False,
                'message': "All provided fields to match against are empty",
                'results': [],
            }

        results = []

        def process_release(r):
            if type(r) == dict:
                return r['title']
            else:
                return r

        # Search MusicBrainz
        mb_results = musicbrainzngs.search_recordings(**musicbrainz_search)
        for recording in mb_results['recording-list']:
            all_releases = [r for r in recording['release-list']]
            if len(album) > 0:
                releases = process.extract(album, all_releases,
                                           processor=process_release)
            else:
                releases = [(r, 0) for r in all_releases]

            for release, _ in releases:
                t = models.Track(
                    title=recording['title'],
                    album=release['title'],
                    artist=recording['artist-credit-phrase'],
                    label="Not Available")
                t.recording_mbid = recording['id']
                t.release_mbid = release['id']
                t.releasegroup_mbid = release['release-group']['id']

                artist_credits = recording.get('artist-credit', [])
                if len(artist_credits) == 1:
                    t.artist_mbid = artist_credits[0]['artist']['id']
                results.append(t.serialize())

#        # Search local database
#        tracks = tracks.limit(8).all()
#        if len(tracks) == 0:
#            tracks = base_query
#
#            # if there are too few results, append some similar results
#            artist = request.args.get('artist', '').strip()
#            if len(artist) > 0:
#                somesearch = True
#                tracks = tracks.filter(
#                    models.Track.artist.ilike(''.join(['%', artist, '%'])))
#
#            title = request.args.get('title', '').strip()
#            if len(title) > 0:
#                somesearch = True
#                tracks = tracks.filter(
#                    models.Track.title.ilike(''.join(['%', title, '%'])))
#
#            album = request.args.get('album', '').strip()
#            if len(album) > 0:
#                somesearch = True
#                tracks = tracks.filter(
#                    models.Track.album.ilike(''.join(['%', album, '%'])))
#
#            label = request.args.get('label', '').strip()
#            if len(label) > 0:
#                somesearch = True
#                tracks = tracks.filter(
#                    models.Track.label.ilike(''.join(['%', label, '%'])))
#
#            tracks = tracks.limit(8).all()
#
#        if len(tracks) > 0:
#            results += [t.serialize() for t in tracks]

        return {
            'success': True,
            'results': results,
        }


class TrackAutoComplete(TrackmanResource):
    def get(self):
        """
        Search the track database for a particular field
        ---
        operationId: autocompleteTracks
        tags:
        - trackman
        - track
        parameters:
        - in: query
          name: artist
          type: string
          description: Partial artist name
        - in: query
          name: title
          type: string
          description: Partial track title
        - in: query
          name: album
          type: string
          description: Partial album title
        - in: query
          name: label
          type: string
          description: Partial record label
        - in: query
          name: field
          type: string
          required: true
          description: The field to autocomplete
        responses:
          200:
            description: Search results
            schema:
              type: object
              properties:
                success:
                  type: boolean
                results:
                  type: array
          400:
            description: Bad request
        """

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
            return {
                'success': False,
                'message': "Unknown field provided to use for autocomplete",
                'results': [],
            }

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
            return {
                'success': False,
                'message': "All provided fields to match against are empty",
                'results': [],
            }

        # Check if results

        tracks = tracks.limit(25).all()
        if len(tracks) > 0:
            results = [t[0] for t in tracks]
        else:
            results = []

        return {
            'success': True,
            'results': results,
        }


class TrackList(TrackmanResource):
    def post(self):
        """
        Create a new track in the database
        ---
        operationId: createTrack
        tags:
        - trackman
        - track
        parameters:
        - in: form
          name: artist
          type: string
          required: true
          description: Artist name
        - in: form
          name: title
          type: string
          required: true
          description: Track title
        - in: form
          name: album
          type: string
          required: true
          description: Album title
        - in: form
          name: label
          type: string
          required: true
          description: Record label
        responses:
          201:
            description: Track created
            schema:
              type: object
              properties:
                success:
                  type: boolean
                track_id:
                  type: integer
                  description: The ID of the track
          400:
            description: Bad request
        """

        form = TrackAddForm(meta={'csrf': False})
        if form.validate():
            track = find_or_add_track(models.Track(
                form.title.data,
                form.artist.data,
                form.album.data,
                form.label.data))

            return {
                'success': True,
                'track_id': track.id,
            }, 201
        else:
            abort(400, success=False, errors=form.errors,
                  message="The track information you entered did not validate. Common reasons for this include missing or improperly entered information, especially the label. Please try again. If you continue to get this message after several attempts, and you're sure the information is correct, please contact the IT staff for help.")
