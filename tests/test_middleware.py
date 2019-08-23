"""Test Auth Server Middleware."""

import pytest
import json
from expects import expect, be, equal, raise_error, be_above_or_equal, contain, have_key
from datetime import datetime

from strawman import db
from strawman.db import User
from strawman.middleware import process_request, process_response


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
            user1.date_registered = datetime.now()
            db.session.add(user1)
            db.session.commit()

            user2 = User(
                firstname='Mary',
                lastname='Doe',
                age=12
            )
            user2.ssn = '246771234'
            user2.middlename = 'Jane'
            user2.date_registered = datetime.now()
            db.session.add(user2)
            db.session.commit()

            user3 = User(
                firstname='Anthony',
                lastname='Doe',
                age=20
            )
            user3.ssn = '21771294'
            user3.middlename = 'Paul'
            user3.date_registered = datetime.now()
            db.session.add(user3)
            db.session.commit()

            test_scope = scopes[len(scopes) - 1]['scope']['ruleset'][0]['rule']
            responses = process_response(test_scope, User)

            # only two records returned since younger than 18 is not allowed
            expect(len(responses)).to(be(2))

            # social security numbers redacted for all users
            for response in responses:
                expect(response).not_to(have_key('id'))
                expect(response['ssn']).to(equal('**********'))
                if response['age'] < 45:
                    expect(response['firstname']).to(equal('**********'))
                    expect(response['lastname']).to(equal('**********'))
                    expect(response['middlename']).to(equal('**********'))
                    expect(response['suffix']).to(equal('**********'))
                if response['age'] == 45:
                    expect(response['date_registered']).to(equal('**********'))
            print(responses)
