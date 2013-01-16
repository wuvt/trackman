from flask import abort, flash, jsonify, render_template, redirect, \
        request, url_for, Response
import datetime
import json
import redis
import netaddr

from wuvt import app
from wuvt import db
from wuvt import lib
from wuvt import sse
from wuvt.trackman.models import DJ, DJSet, Track


# TODO: turn automation on and off (when not logged in)
# when logged in, allow logging tracks
# 85 minute timeout


@app.route('/admin/trackman', methods=['GET', 'POST'])
def trackman_login():
    if not request.remote_addr in netaddr.IPSet(app.config['INTERNAL_IPS']):
        abort(403)

    red = redis.StrictRedis()

    if 'dj' in request.form:
        red.set("automation_enabled", "false")

        dj = DJ.query.get(request.form['dj'])
        djset = DJSet(dj.id)
        db.session.add(djset)
        db.session.commit()

        return redirect(url_for('trackman_log', setid=djset.id))

    automation = red.get('automation_enabled') == "true"

    djs = DJ.query.filter(DJ.visible == True).order_by(DJ.airname).all()
    return render_template('admin/trackman_login.html', automation=automation,
            djs=djs)


@app.route('/trackman/automation/start', methods=['POST'])
def trackman_start_automation():
    if not request.remote_addr in netaddr.IPSet(app.config['INTERNAL_IPS']):
        abort(403)

    red = redis.StrictRedis()
    red.set('automation_enabled', "true")

    flash("Automation started")
    return redirect(url_for('trackman_login'))


@app.route('/admin/trackman/log/<int:setid>', methods=['GET', 'POST'])
def trackman_log(setid):
    djset = DJSet.query.get_or_404(setid)

    errors = {}

    if 'artist' in request.form:
        artist = request.form['artist'].strip()
        if len(artist) <= 0:
            errors['artist'] = "You must enter an artist."

        title = request.form['title'].strip()
        if len(title) <= 0:
            errors['title'] = "You must enter a song title."

        album = request.form['album'].strip()
        if len(album) <= 0:
            errors['album'] = "You must enter an album."

        label = request.form['label'].strip()
        if len(label) <= 0:
            errors['label'] = "You must enter a label."

        if len(errors.items()) <= 0:
            track = Track(djset.dj_id, djset.id, title, artist, album, label,
                    'request' in request.form, 'vinyl' in request.form)
            db.session.add(track)
            db.session.commit()

            # send server-sent event
            sse.send(json.dumps({'event': "track_change", 'track':
                track.serialize()}))

            flash("Track logged")

    return render_template('admin/trackman_log.html', djset=djset)


@app.route('/admin/trackman/log/<int:setid>/end', methods=['POST'])
def trackman_logout(setid):
    djset = DJSet.query.get_or_404(setid)
    djset.dtend = datetime.datetime.now()
    db.session.commit()

    return redirect(url_for('trackman_login'))