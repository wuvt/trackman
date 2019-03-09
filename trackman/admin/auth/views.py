from flask import flash, jsonify, make_response, redirect, \
    render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from trackman import app, auth_manager, db
from trackman.admin import bp
from trackman.auth.models import UserRole, GroupRole


@bp.route('/roles/users/add', methods=['GET', 'POST'])
@auth_manager.check_access('admin')
def role_add_user():
    error_fields = []

    if request.method == 'POST':
        role = request.form['role']
        if role not in auth_manager.all_roles:
            error_fields.append('role')

        if len(error_fields) <= 0:
            sub = request.form['sub']

            existing = UserRole.query.filter_by(
                sub=sub, role=role).count()
            if existing > 0:
                flash("That role was already assigned to that user.")
            else:
                db.session.add(UserRole(sub, role))

                try:
                    db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
                    raise

                flash("The role has been assigned to the user.")

            return redirect(url_for('.roles'), 303)

    return render_template('admin/role_add_user.html',
                           roles=sorted(auth_manager.all_roles),
                           error_fields=error_fields)


@bp.route('/roles/users/remove/<int:id>', methods=['POST', 'DELETE'])
@auth_manager.check_access('admin')
def role_remove_user(id):
    user_role = UserRole.query.get_or_404(id)
    db.session.delete(user_role)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    if request.method == 'DELETE' or request.wants_json():
        return jsonify({
            '_csrf_token': app.jinja_env.globals['csrf_token'](),
        })
    else:
        return redirect(url_for('.roles', 303))


@bp.route('/roles/groups/add', methods=['GET', 'POST'])
@auth_manager.check_access('admin')
def role_add_group():
    error_fields = []

    if request.method == 'POST':
        role = request.form['role']
        if role not in auth_manager.all_roles:
            error_fields.append('role')

        group = request.form['group'].strip()
        if len(request.form['group']) <= 0 or len(group) > 254:
            error_fields.append('group')

        if len(error_fields) <= 0:
            existing = GroupRole.query.filter_by(
                group=group, role=role).count()
            if existing > 0:
                flash("That role was already assigned to that group.")
            else:
                db.session.add(GroupRole(group, role))
                try:
                    db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
                    raise

                flash("The role has been assigned to the group.")

            return redirect(url_for('.roles'), 303)

    return render_template('admin/role_add_group.html',
                           roles=sorted(auth_manager.all_roles),
                           error_fields=error_fields)


@bp.route('/roles/groups/remove/<int:id>', methods=['POST', 'DELETE'])
@auth_manager.check_access('admin')
def role_remove_group(id):
    group_role = GroupRole.query.get_or_404(id)
    db.session.delete(group_role)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    if request.method == 'DELETE' or request.wants_json():
        return jsonify({
            '_csrf_token': app.jinja_env.globals['csrf_token'](),
        })
    else:
        return redirect(url_for('.roles', 303))


@bp.route('/roles')
@auth_manager.check_access('admin')
def roles():
    user_roles = UserRole.query.order_by('role').all()
    group_roles = GroupRole.query.order_by('role').all()

    return render_template('admin/roles.html', user_roles=user_roles,
                           group_roles=group_roles)


@bp.route('/js/roles.js')
@auth_manager.check_access('admin')
def roles_js():
    resp = make_response(render_template('admin/roles.js'))
    resp.headers['Content-Type'] = "application/javascript; charset=utf-8"
    return resp
