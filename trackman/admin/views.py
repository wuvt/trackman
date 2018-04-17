from flask import render_template

from trackman.auth import login_required
from trackman.admin import bp
from trackman.admin.auth import views as auth_views


@bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')
