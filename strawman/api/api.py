"""Strawman API"""

from flask import Blueprint
from flask_restful import Api, Resource
from strawman.db import db
from strawman.middleware import protected_resource, can_access
from strawman.utilities import ResponseBody


class UserResource(Resource):
    """A simple user resource."""

    def __init__(self):
        self.response_body = ResponseBody()

    def get(self, id: str = None):
        is_valid_request, scope = can_access()
        if is_valid_request:
            if hasattr(scope, 'restricted_fields'):
                print('Restricted Fields')
            if hasattr(scope, 'redacted_fields'):
                print('Redacted Fields')
            if hasattr(scope, 'access_policies'):
                print('Access Policies')
            return self.response_body.get_one_response(result=dict())
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
