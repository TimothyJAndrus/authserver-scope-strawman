"""Database Models."""

from uuid import uuid4
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql.json import JSONB

db = SQLAlchemy()
ma = Marshmallow()

roles = db.Table('roles',
                 db.Column('client_id', db.String, db.ForeignKey('clients.id'), primary_key=True),
                 db.Column('role_id', db.String, db.ForeignKey('oauth2_roles.id'), primary_key=True))


class User(db.Model):
    """A simple user model for testing the strawman."""

    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    firstname = db.Column(db.String, nullable=False)
    middlename = db.Column(db.String, nullable=True)
    lastname = db.Column(db.String, nullable=False)
    suffix = db.Column(db.String, nullable=True)
    ssn = db.Column(db.String, nullable=True)
    age = db.Column(db.Integer, nullable=False)
    date_registered = db.Column(db.TIMESTAMP)

    def __init__(self, firstname: str, lastname: str, age: int, middlename: str = None):
        self.id = str(uuid4()).replace('-', '')
        self.firstname = firstname
        self.lastname = lastname
        self.age = age

    def __str__(self):
        return '{} {}'.format(self.firstname, self.lastname)


class Role(db.Model):
    """OAuth 2.0 Role."""

    __tablename__ = 'oauth2_roles'
    __table_args__ = (db.UniqueConstraint('role'), )

    id = db.Column(db.String, primary_key=True)
    role = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    rules = db.Column(JSONB)
    active = db.Column(db.Boolean)
    date_created = db.Column(db.TIMESTAMP)
    date_last_updated = db.Column(db.TIMESTAMP)

    def __init__(self, role, description, rules=None, active=True):
        self.id = str(uuid4()).replace('-', '')
        self.role = role
        self.description = description
        self.rules = rules
        self.active = active
        self.date_created = datetime.utcnow()
        self.date_last_updated = datetime.utcnow()

    def __str__(self):
        return self.id


class Client(db.Model):
    """A mock client that gets one or more scopes."""

    __tablename__ = 'clients'
    id = db.Column(db.String, primary_key=True)
    client_name = db.Column(db.String)
    client_id = db.Column(db.String)
    client_secret = db.Column(db.String)
    roles = db.relationship('Role', secondary=roles, lazy='subquery',
                            backref=db.backref('clients', lazy=True))
