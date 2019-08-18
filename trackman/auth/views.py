from flask import Blueprint, redirect, session
from trackman.auth import login_required, logout_user


bp = Blueprint('auth', __name__)


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('access', None)

    return redirect('/')
