import abc
import datetime
from .mixins import UserMixin


class AuthDataStore(abc.ABC):
    @abc.abstractmethod
    def get_session_by_token(self, session_token: str):
        return NotImplemented

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

    @abc.abstractmethod
    def list_sessions_for_user(self, user_id: str):
        return NotImplemented

    @abc.abstractmethod
    def delete_session_by_token(self, session_token: str):
        return NotImplemented

    @abc.abstractmethod
    def delete_session_for_user_by_id(self, user_id: str, session_id: int):
        return NotImplemented

    @abc.abstractmethod
    def delete_sessions_for_user(self, user_id: str):
        return NotImplemented

    @abc.abstractmethod
    def delete_sessions_by_expiration(self, expires: datetime.datetime):
        return NotImplemented

    @abc.abstractmethod
    def commit(self):
        return NotImplemented
