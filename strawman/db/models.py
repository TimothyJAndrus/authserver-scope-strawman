"""Database Models."""

from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from uuid import uuid4

db = SQLAlchemy()
ma = Marshmallow()


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



