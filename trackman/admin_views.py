from flask import current_app, flash, jsonify, render_template, \
        redirect, request, session, url_for, make_response, abort, Response
import datetime
import hmac

from . import db, redis_conn
from .auth import current_user
from .blueprints import private_bp
from .forms import DJRegisterForm, DJReactivateForm
from .lib import enable_automation, renew_dj_lease, generate_claim_token
from .mail import send_claim_email
from .models import DJ, DJSet, DJClaim, DJClaimToken
from .view_utils import dj_only


@private_bp.route('/', methods=['GET', 'POST'])
@dj_only
def login():
    if 'dj' in request.form and len(request.form['dj']) > 0:
        if current_user.is_authenticated:
            claim = DJClaim.query.join(DJ).filter(
                DJ.id == request.form['dj'],
                DJClaim.sub == current_user.sub).scalar()
            if claim is None:
                abort(403)

        dj = DJ.query.get(request.form['dj'])

        current_app.logger.warning(
            "Trackman: {airname} logged in from {ip} using {ua}".format(
                airname=dj.airname,
                ip=request.remote_addr,
                ua=request.user_agent))

        session['dj_id'] = dj.id
        renew_dj_lease()

        return redirect(url_for('.log'))

    automation = redis_conn.get('automation_enabled') == b"true"

    onair_djset_id = redis_conn.get('onair_djset_id')
    if onair_djset_id is not None:
        onair_djset = DJSet.query.get(int(onair_djset_id))
        if onair_djset.dj_id <= 1:
            onair_djset = None
    else:
        onair_djset = None

    if current_user.is_authenticated:
        djs = DJ.query.join(DJ.claims).filter(DJClaim.sub == current_user.sub)
    else:
        djs = DJ.query.filter(DJ.id > 1, DJ.visible == True)

    djs = djs.order_by(DJ.airname).all()
    return render_template('login.html',
                           automation=automation, onair_djset=onair_djset,
                           djs=djs)


@private_bp.route('/login/all', methods=['GET', 'POST'])
@dj_only
def login_all():
    if 'dj' in request.form and len(request.form['dj']) > 0:
        if int(request.form['dj']) == 1:
            # start automation if we selected DJ with ID 1
            return redirect(url_for('.start_automation'), 307)

        if current_user.is_authenticated:
            claim = DJClaim.query.join(DJ).filter(
                DJ.id == request.form['dj'],
                DJClaim.sub == current_user.sub).scalar()
            if claim is None:
                # start the DJ claim flow
                dj = DJ.query.get(int(request.form['dj']))
                token = generate_claim_token()

                claim_token = DJClaimToken(
                    dj.id, current_user.sub, dj.email, token)
                db.session.add(claim_token)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise

                send_claim_email(claim_token, request.remote_addr)
                flash("An email with information on how to complete the "
                      "claim process has been sent to the address associated "
                      "with that DJ.")
                return redirect(url_for('.login'))

        dj = DJ.query.get(request.form['dj'])
        dj.visible = True
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        current_app.logger.warning(
            "Trackman: {airname} logged in from {ip} using {ua}".format(
                airname=dj.airname,
                ip=request.remote_addr,
                ua=request.user_agent))

        session['dj_id'] = dj.id
        renew_dj_lease()

        return redirect(url_for('.log'))

    automation = redis_conn.get('automation_enabled') == b"true"

    onair_djset_id = redis_conn.get('onair_djset_id')
    if onair_djset_id is not None:
        onair_djset = DJSet.query.get(int(onair_djset_id))
        if onair_djset.dj_id <= 1:
            onair_djset = None
    else:
        onair_djset = None

    djs = DJ.query.filter(DJ.id > 1).order_by(DJ.airname).all()
    return render_template('login_all.html',
                           automation=automation, onair_djset=onair_djset,
                           djs=djs)


@private_bp.route('/automation/start', methods=['POST'])
@dj_only
def start_automation():
    automation = redis_conn.get('automation_enabled') == b"true"
    if not automation:
        current_app.logger.warning(
            "Trackman: Start automation from {ip} using {ua}".format(
                ip=request.remote_addr,
                ua=request.user_agent))

        enable_automation()

    return redirect(url_for('.login'))


@private_bp.route('/log')
@dj_only
def log():
    dj_id = session.get('dj_id', None)
    if dj_id is None:
        return redirect(url_for('.login'))

    dj = DJ.query.get_or_404(dj_id)
    if dj.phone is None or dj.email is None:
        return redirect(url_for('.reactivate_dj'))

    djset_id = session.get('djset_id', None)
    if djset_id is not None:
        djset = DJSet.query.get_or_404(djset_id)
        if djset.dtend is not None:
            # This is a logged out DJSet
            session.pop('djset_id', None)

    renew_dj_lease()

    return render_template('log.html',
                           dj=dj)


@private_bp.route('/js/log.js')
@dj_only
def log_js():
    dj_id = session.get('dj_id', None)
    if dj_id is None:
        abort(404)

    djset_id = session.get('djset_id', None)

    resp = make_response(render_template('log.js',
                         dj_id=dj_id, djset_id=djset_id))
    resp.headers['Content-Type'] = "application/javascript; charset=utf-8"
    return resp


@private_bp.route('/register', methods=['GET', 'POST'])
@dj_only
def register():
    form = DJRegisterForm()

    if current_user.is_authenticated:
        form.name.default = current_user.id_token['name']
        form.email.default = current_user.id_token['email']

    if form.is_submitted():
        if form.validate():
            newdj = DJ(form.airname.data, form.name.data)
            newdj.email = form.email.data
            newdj.phone = form.phone.data
            newdj.genres = form.genres.data
            db.session.add(newdj)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

            if current_user.is_authenticated:
                claim = DJClaim(newdj.id, current_user.sub)
                db.session.add(claim)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise

            if request.wants_json():
                return jsonify(success=True)
            else:
                flash("DJ added.")
                return redirect(url_for('.login'))
        elif request.wants_json():
            return jsonify(success=False, errors=form.errors)

    return render_template(
        'register.html',
        form=form)


@private_bp.route('/reactivate_dj', methods=['GET', 'POST'])
@dj_only
def reactivate_dj():
    dj_id = session.get('dj_id', None)
    if dj_id is None:
        return redirect(url_for('.login'))

    dj = DJ.query.get_or_404(dj_id)
    form = DJReactivateForm()

    # if neither phone nor email is missing, someone is doing silly things
    if dj.email is not None and dj.phone is not None:
        return redirect(url_for('.log'))

    if form.is_submitted():
        if form.validate():
            dj.email = form.email.data
            dj.phone = form.phone.data
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

            if request.wants_json():
                return jsonify(success=True)
            else:
                return redirect(url_for('.log'))
        elif request.wants_json():
            return jsonify(success=False, errors=form.errors)

    return render_template(
        'reactivate.html',
        form=form,
        dj=dj)


@private_bp.route('/confirm_claim/<int:id>/<string:token>')
@dj_only
def confirm_claim(id, token):
    claim_token = DJClaimToken.query.get_or_404(id)
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(
        seconds=current_app.config['CLAIM_TOKEN_TIMEOUT'])

    if claim_token.request_date >= cutoff and \
            claim_token.sub == current_user.sub and \
            hmac.compare_digest(claim_token.token, token):
        claim = DJClaim(claim_token.dj_id, claim_token.sub)
        db.session.add(claim)
        db.session.delete(claim_token)
        db.session.commit()

        flash("DJ claimed.")
        return redirect(url_for('.login'))
    else:
        return render_template('dj_claim_error.html'), 403


@private_bp.route('/api/live')
@dj_only
def dj_live():
    resp = Response()
    resp.headers['X-Accel-Buffering'] = "no"
    resp.headers['X-Accel-Redirect'] = "/_pubsub/dj/sub"
    return resp
