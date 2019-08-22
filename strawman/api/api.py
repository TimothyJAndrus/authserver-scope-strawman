"""Strawman API"""

import json
from flask import Blueprint
from flask_restful import Api, Resource
from sqlalchemy import text
from strawman.db import db, User
from strawman.middleware import protected_resource, can_access,\
    process_request, process_response
from strawman.utilities import ResponseBody


class UserResource(Resource):
    """A simple user resource."""

    def __init__(self):
        self.response_body = ResponseBody()

    def get(self, id: str = None):
        is_valid_request, scope = can_access()
        if is_valid_request:

            return self.response_body.get_one_response(result=all_users)
        else:
            return self.response_body.custom_response(
                status='Unauthorized', code=401,
                messages=['This client is not authorized to access this resource. If you feel this is an error, please contact your administrator.'])

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
