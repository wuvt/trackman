import datetime
from flask import abort, Blueprint, flash, redirect, render_template, session, url_for
from trackman import db
from . import login_required, logout_user
from .utils import current_user
from .models import UserSession


bp = Blueprint("auth", __name__)


@bp.route("/sessions")
@login_required
def view_sessions():
    sessions = UserSession.query.filter(
        UserSession.sub == current_user.sub,
        UserSession.expires >= datetime.datetime.utcnow(),
    ).order_by(db.desc(UserSession.login_at),)
    return render_template(
        "auth/view_sessions.html",
        sessions=sessions,
        current_session_token=session["user_session_token"],
    )


@bp.route("/sessions/<int:session_id>/revoke", methods=["POST"])
@login_required
def revoke_session(session_id):
    user_session = UserSession.query.get_or_404(session_id)
    if user_session.sub != current_user.sub:
        abort(404)

    db.session.delete(user_session)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    flash("Session revoked.")
    return redirect(url_for(".view_sessions"))


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")

    return render_template("logged_out.html")
