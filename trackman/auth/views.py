from flask import Blueprint, flash, render_template, session
from trackman.auth import login_required, logout_user


bp = Blueprint('auth', __name__)


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('access', None)
    flash("You have been logged out.")

    return render_template('logged_out.html')
