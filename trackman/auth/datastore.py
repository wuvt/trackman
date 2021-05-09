import datetime
from .models import GroupRole, User, UserRole, UserSession


class TrackmanAuthDataStore(object):
    def __init__(self, db):
        self.db = db

    # TODO: should return a proper UserMixin and a list a roles
    def get_session_by_token(self, session_token):
        user_session = UserSession.query.filter(
            UserSession.token == session_token,
        ).one()
        return user_session

    # TODO: we call user_id sub now, what should it actually be?
    # or should this take a user rather than user_id?
    def get_roles_for_user(self, user_id):
        user_roles = set([])
        user_roles_db = UserRole.query.filter(UserRole.sub == user_id)
        for entry in user_roles_db:
            user_roles.add(entry.role)

        return user_roles

    # TODO: not sure whether this is ideal or not
    def get_roles_for_groups(self, group_ids):
        group_roles = set([])
        group_roles_db = GroupRole.query.filter(GroupRole.group.in_(group_ids))
        for entry in group_roles_db:
            group_roles.add(entry.role)

        return group_roles

    # TODO: I'm not sure taking id_token is the best thing here, reevaluate?
    # TODO: should return a proper UserMixin? or what?
    # maybe I should make a UserSessionMixin with user and role properties
    def create_session(self, session_token, id_token, expires, user_agent,
                       remote_addr, roles):
        user_session = UserSession(
            token=session_token,
            id_token=id_token,
            expires=expires,
            user_agent=user_agent,
            remote_addr=remote_addr,
            roles=roles)
        self.db.session.add(user_session)
        self.commit()

        return user_session

    # TODO: we call user_id sub now, what should it actually be?
    def list_sessions_for_user(self, user_id):
        sessions = UserSession.query.filter(
            UserSession.sub == user_id,
            UserSession.expires >= datetime.datetime.utcnow(),
        ).order_by(db.desc(UserSession.login_at),)
        return sessions

    def delete_session_by_token(self, token):
        user_session = self.get_session_by_token(session_token)
        if user_session is not None:
            self.db.session.delete(user_session)
            self.commit()

    def delete_session_for_user_by_id(self, user_id, session_id):
        user_session = UserSession.query.get(session_id)
        if user_session.sub != user_id:
            return None

        self.db.session.delete(user_session)
        self.commit()
        return user_session

    # TODO: we call user_id sub now, what should it actually be?
    def delete_sessions_for_user(self, user_id):
        sessions = UserSession.query.filter_by(sub=user_id).all()
        for session in sessions:
            self.db.session.delete(session)
        self.commit()

    def delete_sessions_by_expiration(self, expires):
        user_sessions = UserSession.query.filter(UserSession.expires <= expires)
        for user_session in user_sessions:
            self.db.session.delete(user_session)
        self.commit()

    def commit(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
