from flask import current_app, flash, redirect, render_template, request, \
    url_for
from wtforms import ValidationError
import csv
import dateutil.parser
import io

from trackman import auth_manager, db, format_datetime
from trackman.auth import login_required
from trackman.admin import bp
from trackman.admin.auth import views as auth_views
from trackman.forms import DJRegisterForm, DJAdminEditForm
from trackman.models import DJ, TrackLog


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

    return render_template('admin/dj_edit.html', dj=dj, form=form)


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