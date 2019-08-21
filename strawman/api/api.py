"""Strawman API"""

from flask import Blueprint
from flask_restful import Api, Resource
from strawman.db import db


class UserResource(Resource):
    """A simple user resource."""

    def get(self, id: str = None):
        pass

    def post(self, id=None):
        pass

    def put(self, id: str = None):
        pass

    def patch(self, id: str = None):
        pass

    def delete(self, id: str = None):
        pass


user_bp = Blueprint('user_ep', __name__)
user_api = Api(user_bp)
user_api.add_resource(UserResource, '/users', '/users/<string:id>')
