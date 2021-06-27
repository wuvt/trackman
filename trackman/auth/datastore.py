import datetime
from .base import AuthDataStore
from .mixins import UserMixin
from .models import GroupRole, UserRole, UserSession


class TrackmanAuthDataStore(AuthDataStore):
    def __init__(self, db):
        self.db = db

    # TODO: should return a proper UserMixin and a list a roles
    def get_session_by_token(self, session_token: str):
        user_session = UserSession.query.filter(
            UserSession.token == session_token,
        ).one()
        return user_session

    # TODO: we call user_id sub now, what should it actually be?
    # or should this take a user rather than user_id?
    def get_roles_for_user(self, user_id: str):
        user_roles = set([])
        user_roles_db = UserRole.query.filter(UserRole.sub == user_id)
        for entry in user_roles_db:
            user_roles.add(entry.role)

        return user_roles

    # TODO: not sure whether this is ideal or not
    def get_roles_for_groups(self, group_ids: list):
        group_roles = set([])
        group_roles_db = GroupRole.query.filter(GroupRole.group.in_(group_ids))
        for entry in group_roles_db:
            group_roles.add(entry.role)

        return group_roles

    def create_session(
        self,
        session_token: str,
        user: UserMixin,
        expires: datetime.datetime,
        user_agent: str,
        remote_addr: str,
        roles: list,
    ):
        user_session = UserSession(
            token=session_token,
            user=user,
            expires=expires,
            user_agent=user_agent,
            remote_addr=remote_addr,
            roles=roles,
        )
        self.db.session.add(user_session)
        self.commit()

        return user_session

    # TODO: we call user_id sub now, what should it actually be?
    def list_sessions_for_user(self, user_id: str):
        sessions = UserSession.query.filter(
            UserSession.sub == user_id,
            UserSession.expires >= datetime.datetime.utcnow(),
        ).order_by(
            self.db.desc(UserSession.login_at),
        )
        return sessions

    def delete_session_by_token(self, session_token: str):
        user_session = self.get_session_by_token(session_token)
        if user_session is not None:
            self.db.session.delete(user_session)
            self.commit()

    def delete_session_for_user_by_id(self, user_id: str, session_id: int):
        user_session = UserSession.query.get(session_id)
        if user_session.sub != user_id:
            return None

        self.db.session.delete(user_session)
        self.commit()
        return user_session

    # TODO: we call user_id sub now, what should it actually be?
    def delete_sessions_for_user(self, user_id: str):
        sessions = UserSession.query.filter_by(sub=user_id).all()
        for session in sessions:
            self.db.session.delete(session)
        self.commit()

    def delete_sessions_by_expiration(self, expires: datetime.datetime):
        user_sessions = UserSession.query.filter(UserSession.expires <= expires)
        for user_session in user_sessions:
            self.db.session.delete(user_session)
        self.commit()

    def commit(self):
        try:
            self.db.session.commit()
        except:
            self.db.session.rollback()
            raise
