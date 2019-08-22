"""Auth Decorator and Middleware."""

import re
import json
from functools import wraps
from flask import request

from strawman.utilities import ResponseBody
from strawman.db import Client, Role, User, Token


def verify_client_token_and_scopes(token: str):
    # determine if the token is valid
    token = Token.query.filter_by(token=token).first()
    if not token:
        return False

    # determine which client currently holds the token
    client_id = token.client_id
    client = Client.query.filter_by(id=client_id).first()
    if not client:
        return False

    # get scopes held by client
    client_scopes = client.roles
    if len(client_scopes) == 0:
        return False

    # determine if scopes allow the kind of access requested
    #
    method_allowed = False
    candidate_rules = []
    for scope in client_scopes:
        rules = json.loads(scope.rules)
        for rule in rules['ruleset']:
            _rule = rule['rule']
            # evaluate the resource to see if the rule applies
            if re.match(_rule['resource'], request.url):
                # check if method is allowed
                if request.method in _rule['allowed_methods'] or _rule['allowed_methods'][0] == '*':
                    method_allowed = True
                    candidate_rules.append(rule)
                else:
                    # important because we prefer to err on the side of no access if a contradictory rule is found
                    method_allowed = False
                    break
    return method_allowed, candidate_rules[0]


def can_access():
    token = None
    try:
        token = request.headers.get('Authorization', None)
        if token:
            token = re.split('\\s+', token)
            if len(token) != 2:
                print('Invalid Bearer Token Header')
            if str(token[0]).upper() == 'BEARER':
                token = token[1]
                if not verify_client_token_and_scopes(token):
                    raise Exception('Invalid Token or Scope')
            else:
                raise Exception('No Bearer Token')
        else:
            raise Exception('No Access Token')
    except Exception as e:
        return False, None

    if token:
        return verify_client_token_and_scopes(token)
    else:
        return False, None


def protected_resource():
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            if can_access():
                return f(*args, **kwargs)
            else:
                return ResponseBody().custom_response(
                    status='Unauthorized', code=401,
                    messages=['This client is not authorized to access this resource. If you feel this is an error, please contact your administrator.'])

        return wrapped_f
    return wrap
