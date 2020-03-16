from flask import current_app, flash, redirect, render_template, request, \
    url_for, abort
import csv
import dateutil.parser
import io

from trackman import auth_manager, db, format_datetime
from trackman.auth import login_required
from trackman.admin import bp
from trackman.admin.auth import views as auth_views  # noqa: F401
from trackman.forms import DJRegisterForm, DJAdminEditForm, RotationForm, \
    RotationEditForm, DJDeleteClaimForm
from trackman.models import DJ, DJClaim, Rotation, TrackLog


@bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')


@bp.route('/djs')
@bp.route('/djs/page<int:page>')
@auth_manager.check_access('admin')
def djs(page=1):
    djs = DJ.query.order_by(DJ.airname).paginate(
        page, current_app.config['ARTISTS_PER_PAGE'])
    return render_template('admin/djs.html', djs=djs)


@bp.route('/djs/add', methods=['GET', 'POST'])
@auth_manager.check_access('admin')
def dj_add():
    form = DJRegisterForm()
    if form.validate_on_submit():
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

        flash('DJ added.')
        return redirect(url_for('admin.djs'), 303)

    return render_template('admin/dj_add.html', form=form)


@bp.route('/djs/<int:id>', methods=['GET', 'POST'])
@auth_manager.check_access('admin')
def dj_edit(id):
    dj = DJ.query.get_or_404(id)
    form = DJAdminEditForm()
    form.dj = dj

    claims = DJClaim.query.filter_by(dj_id=dj.id).all()

    if form.validate_on_submit():
        dj.airname = form.airname.data
        dj.name = form.name.data

        if dj.id > 1:
            dj.email = form.email.data
            dj.phone = form.phone.data
            dj.genres = form.genres.data
            dj.visible = form.visible.data

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        flash('DJ edited.')
        return redirect(url_for('admin.djs'), 303)

    return render_template('admin/dj_edit.html', dj=dj, form=form,
                           claims=claims)


@bp.route('/djs/<int:dj_id>/claims', methods=['GET', 'POST'])
@auth_manager.check_access('admin')
def dj_edit_claims(dj_id):
    dj = DJ.query.get_or_404(dj_id)
    form = DJDeleteClaimForm()
    form.dj = dj

    if form.validate_on_submit():
        claim = DJClaim.query.get_or_404(form.claim_id.data)
        if claim.dj_id != dj_id:
            abort(404)

        db.session.delete(claim)

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        flash('DJ claim deleted.')

    return redirect(url_for('admin.dj_edit', id=dj_id), 303)


@bp.route('/reports')
@auth_manager.check_access('library')
def reports():
    return render_template('admin/reports.html')


@bp.route('/reports/bmi', methods=['GET', 'POST'])
@auth_manager.check_access('library')
def reports_bmi():
    if request.method == 'POST':
        start = dateutil.parser.parse(request.form['dtstart'])
        end = dateutil.parser.parse(request.form['dtend'])
        end = end.replace(hour=23, minute=59, second=59)

        f = io.StringIO()
        writer = csv.writer(f)

        tracks = TrackLog.query.filter(TrackLog.played >= start,
                                       TrackLog.played <= end).all()
        for track in tracks:
            writer.writerow([
                current_app.config['TRACKMAN_NAME'],
                format_datetime(track.played),
                track.track.title,
                track.track.artist,
            ])

        f.seek(0)

        filename = end.strftime("bmirep-%Y-%m-%d.csv")
        return f.read(), {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition":
                "attachment; filename=\"{0}\"".format(filename),
        }
    else:
        return render_template('admin/reports_bmi.html')


@bp.route('/rotations')
@bp.route('/rotations/page<int:page>')
@auth_manager.check_access('admin')
def rotations(page=1):
    rotations = Rotation.query.order_by(Rotation.rotation).paginate(
        page, current_app.config['ARTISTS_PER_PAGE'])
    return render_template('admin/rotations.html', rotations=rotations)


@bp.route('/rotations/add', methods=['GET', 'POST'])
@auth_manager.check_access('admin')
def rotation_add():
    form = RotationForm()
    if form.validate_on_submit():
        rotation = Rotation(form.rotation.data)
        db.session.add(rotation)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        flash('Rotation added.')
        return redirect(url_for('admin.rotations'), 303)

    return render_template('admin/rotation_add.html', form=form)


@bp.route('/rotations/<int:id>', methods=['GET', 'POST'])
@auth_manager.check_access('admin')
def rotation_edit(id):
    rotation = Rotation.query.get_or_404(id)
    form = RotationEditForm()

    if form.validate_on_submit():
        rotation.visible = form.visible.data
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        flash('Rotation edited.')
        return redirect(url_for('admin.rotations'), 303)

    return render_template('admin/rotation_edit.html', rotation=rotation,
                           form=form)
