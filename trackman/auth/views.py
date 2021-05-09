import datetime
from flask import abort, Blueprint, flash, redirect, render_template, session, url_for
from trackman import db
from . import login_required, logout_user
from .utils import current_user


bp = Blueprint("auth", __name__)


@bp.route("/sessions")
@login_required
def view_sessions():
    sessions = datastore.list_sessions_for_user(current_user.sub)
    return render_template(
        "auth/view_sessions.html",
        sessions=sessions,
        current_session_token=session["user_session_token"],
    )


@bp.route("/sessions/<int:session_id>/revoke", methods=["POST"])
@login_required
def revoke_session(session_id):
    user_session = datastore.delete_session_for_user_by_id(
        current_user.sub, session_id)
    if user_session is None:
        abort(404)

    flash("Session revoked.")
    return redirect(url_for(".view_sessions"))


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")

    return render_template("logged_out.html")
