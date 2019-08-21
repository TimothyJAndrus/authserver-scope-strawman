"""Test Fixtures"""

import pytest
import sys
import os
import json
from time import sleep
from flask_migrate import upgrade

from strawman import create_app, db
from strawman.db import Role
from strawman.utilities import PostgreSQLContainer

FULL_ACCESS_SCOPE = {
    "scope": "all:full-access",
    "ruleset": [
        {
            "rule": {
                "resource": "[\\S]+",
                "allowed_methods": [
                    "*"
                ]
            }
        }
    ]
}

READ_ONLY_SCOPE = {
    "scope": "programs:read-only",
    "ruleset": [
        {
            "rule": {
                "resource": "https://sandbox.brighthive.net/programs",
                "allowed_methods": [
                    "GET"
                ],
                "restricted_fields": [
                    {
                        "field": "program_address",
                        "request": True,
                        "response": True
                    }
                ]
            }
        }
    ]
}

REDACTION_SCOPE = {
    "scope": "get:participants-redaction",
    "ruleset": [
        {
            "rule": {
                "resource": "https://sandbox.brighthive.net/participants",
                "allowed_methods": [
                    "GET",
                ],
                "restricted_fields": [
                    {
                        "field": "participation_address",
                        "request": True,
                        "response": True
                    }
                ],
                "redacted_fields": [
                    {
                        "field": "ssn",
                        "policy": "*"
                    },
                ]
            }
        }
    ]
}

REDACTION_ACCESS_POLICY_SCOPE = {
    "scope": "get:participants-id-only-redaction",
    "ruleset": [
        {
            "rule": {
                "resource": "https://sandbox.brighthive.net/participants",
                "allowed_methods": []
            }
        },
        {
            "rule": {
                "resource": "https://sandbox.brighthive.net/participants/[\\w]+",
                "allowed_methods": [
                    "GET"
                ],
                "restricted_fields": [
                    {
                        "field": "participant_address",
                        "request": True,
                        "response": True
                    }
                ],
                "access_policies": [
                    {
                        "description": "description of policy",
                        "policy": "${age} < 18",
                        "mode": "redact"
                    }
                ]
            }
        }
    ]
}

RESTRICTION_ACCESS_POLICY_SCOPE = {
    "scope": "get:participants-id-only-restriction",
    "ruleset": [
        {
            "rule": {
                "resource": "https://sandbox.brighthive.net/participants",
                "allowed_methods": []
            }
        },
        {
            "rule": {
                "resource": "https://sandbox.brighthive.net/participants/[\\w]+",
                "allowed_methods": [
                    "GET"
                ],
                "restricted_fields": [
                    {
                        "field": "participant_address",
                        "request": True,
                        "response": True
                    }
                ],
                "access_policies": [
                    {
                        "description": "description of policy",
                        "policy": "${age} < 18",
                        "mode": "restrict"
                    }
                ]
            }
        }
    ]
}

ALL_SCOPES = [
    FULL_ACCESS_SCOPE,
    READ_ONLY_SCOPE,
    REDACTION_SCOPE,
    REDACTION_ACCESS_POLICY_SCOPE,
    RESTRICTION_ACCESS_POLICY_SCOPE
]


@pytest.fixture(scope='session')
def client():
    """Setup the Flask application and return an instance of the test client.

    Returns:
        client (object): The Flask test client for the application under test.

    """

    app = create_app()
    client = app.test_client()
    return client


@pytest.fixture(scope='session', autouse=True)
def app():
    """Setup the PostgreSQL database instance and return a Flask application.

    Returns:
        app (object): The Flask application.

    """

    DOCKER_CONFIGURATION = {
        'postgres_user': 'test_user',
        'postgres_password': 'test_password',
        'postgres_database': 'test_db',
        'postgres_port': 5433,
        'postgres_image': 'postgres:11.4',
        'container_name': 'postgres_auth_strawman_test'
    }

    postgres_url = 'postgresql://{}:{}@{}:{}/{}'.format(DOCKER_CONFIGURATION['postgres_user'],
                                                        DOCKER_CONFIGURATION['postgres_password'], 'localhost',
                                                        DOCKER_CONFIGURATION['postgres_port'],
                                                        DOCKER_CONFIGURATION['postgres_database'])

    app = create_app(database_url=postgres_url)
    postgres = PostgreSQLContainer(DOCKER_CONFIGURATION)
    postgres.start_container()
    upgraded = False

    with app.app_context():
        while not upgraded:
            try:
                upgrade()
                upgraded = True
            except Exception as e:
                sleep(1)

        # Pre-populate scopes
        for scope in ALL_SCOPES:
            role = Role(role=scope['scope'], description='a test role', rules=json.dumps(scope))
            db.session.add(role)
            db.session.commit()
    yield app
    postgres.stop_container()
