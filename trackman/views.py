from flask import jsonify, render_template, request, send_from_directory, \
        Response
import redis.exceptions
import sqlalchemy.exc

from . import app, db, redis_conn
from .view_utils import IPAccessDeniedException


@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(400)
def error400(error):
    if request.wants_json():
        return jsonify({'errors': "400 Bad Request"}), 400

    return render_template('error400.html'), 400


@app.errorhandler(403)
def error403(error):
    if request.wants_json():
        return jsonify({'errors': "403 Forbidden"}), 403

    return render_template('error403.html'), 403


@app.errorhandler(404)
def error404(error):
    if request.wants_json():
        return jsonify({'errors': "404 Not Found"}), 404

    return render_template('error404.html'), 404


@app.errorhandler(405)
def error405(error):
    if request.wants_json():
        return jsonify({'errors': "405 Method Not Allowed"}), 405

    return render_template('error405.html'), 405


@app.errorhandler(IPAccessDeniedException)
def error403_ipaccess(error):
    if request.wants_json():
        return jsonify({'errors': "403 Forbidden"}), 403

    return render_template('error403.html'), 403


@app.errorhandler(500)
def error500(error):
    if request.wants_json():
        return jsonify({'errors': "500 Internal Server Error"}), 500

    return send_from_directory(app.static_folder, '500.html'), 500


@app.route('/healthz')
def healthcheck():
    try:
        db_status = db.session.scalar(db.select([1]))
    except sqlalchemy.exc.DBAPIError:
        db_status = None

    try:
        redis_status = redis_conn.info()
    except redis.exceptions.ConnectionError:
        redis_status = None

    if db_status is not None and redis_status is not None:
        return "OK"
    else:
        return "fail", 500


@app.route('/live')
def live():
    resp = Response()
    resp.headers['X-Accel-Buffering'] = "no"
    resp.headers['X-Accel-Redirect'] = "/_pubsub/sub"
    return resp
