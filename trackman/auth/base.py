import abc
import datetime
from .mixins import UserMixin


class AuthDataStore(abc.ABC):
    @abc.abstractmethod
    def get_session_by_token(self, session_token: str):
        return NotImplemented

    # TODO: we call user_id sub now, what should it actually be?
    # or should this take a user rather than user_id?
    @abc.abstractmethod
    def get_roles_for_user(self, user_id: str):
        return NotImplemented

    @abc.abstractmethod
    def get_roles_for_groups(self, group_ids: list):
        return NotImplemented

    @abc.abstractmethod
    def create_session(
        self,
        session_token: str,
        user: UserMixin,
        expires: datetime.datetime,
        user_agent: str,
        remote_addr: str,
        roles: list,
    ):
        return NotImplemented

    # TODO: we call user_id sub now, what should it actually be?
    @abc.abstractmethod
    def list_sessions_for_user(self, user_id: str):
        return NotImplemented

    @abc.abstractmethod
    def delete_session_by_token(self, session_token: str):
        return NotImplemented

    # TODO: we call user_id sub now, what should it actually be?
    @abc.abstractmethod
    def delete_session_for_user_by_id(self, user_id: str, session_id: int):
        return NotImplemented

    # TODO: we call user_id sub now, what should it actually be?
    @abc.abstractmethod
    def delete_sessions_for_user(self, user_id: str):
        return NotImplemented

    @abc.abstractmethod
    def delete_sessions_by_expiration(self, expires: datetime.datetime):
        return NotImplemented

    @abc.abstractmethod
    def commit(self):
        return NotImplemented
