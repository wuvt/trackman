import datetime
from flask import json
from trackman import db
from .mixins import UserMixin
from werkzeug.useragents import UserAgent


class User(UserMixin):
    def __init__(self, id_token):
        self.sub = id_token['sub']
        self.id_token = id_token

    @property
    def name(self):
        return self.id_token['name']

    @property
    def email(self):
        return self.id_token['email']


class UserRole(db.Model):
    __tablename__ = "user_role"
    id = db.Column(db.Integer, primary_key=True)
    sub = db.Column(db.Unicode(255), nullable=False)
    role = db.Column(db.Unicode(255), nullable=False)

    def __init__(self, sub, role):
        self.sub = sub
        self.role = role


class UserSession(db.Model):
    __tablename__ = "user_session"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    sub = db.Column(db.Unicode(255), nullable=False)
    id_token = db.Column(db.UnicodeText)
    login_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires = db.Column(db.DateTime)
    user_agent = db.Column(db.Unicode(512))
    remote_addr = db.Column(db.Unicode(100))
    roles_list = db.Column(db.Unicode(1024))

    def __init__(self, token, id_token, expires, user_agent, remote_addr,
                 roles):
        self.token = token
        self.sub = id_token['sub']
        self.id_token = json.dumps(id_token)
        self.expires = expires
        self.user_agent = user_agent
        self.remote_addr = remote_addr
        self.roles_list = ','.join(roles)

    @property
    def roles(self):
        return set(self.roles_list.split(','))

    def parse_user_agent(self):
        return UserAgent(self.user_agent)


class GroupRole(db.Model):
    __tablename__ = "group_role"
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.Unicode(255), nullable=False)
    role = db.Column(db.Unicode(255), nullable=False)

    def __init__(self, group, role):
        self.group = group
        self.role = role
