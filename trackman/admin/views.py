from flask import flash, redirect, render_template, url_for
from wtforms import ValidationError

from trackman import auth_manager, db
from trackman.auth import login_required
from trackman.admin import bp
from trackman.admin.auth import views as auth_views
from trackman.forms import DJRegisterForm, DJAdminEditForm
from trackman.models import DJ


@bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')


@bp.route('/djs')
@auth_manager.check_access('admin')
def djs():
    djs = DJ.query.order_by(DJ.airname).all()
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
