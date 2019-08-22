"""Test Auth Server Middleware."""

import pytest
import json
from flask import Response
from strawman import db
from strawman.db import User
from strawman.middleware import process_request, process_response
from expects import expect, be, equal, raise_error, be_above_or_equal, contain


class TestAuthMiddleware(object):
    def test_middleware(self, app, scopes):
        with app.app_context():
            user1 = User(
                firstname='John',
                lastname='Doe',
                age=45
            )
            user1.ssn = '123456789'
            user1.middlename = 'Evan'
            db.session.add(user1)
            db.session.commit()

            process_response(scopes[3]['ruleset'][1]['rule'], User)
