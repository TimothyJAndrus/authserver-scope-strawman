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
                "resource": "http://localhost:8000/users",
                "allowed_methods": [
                    "GET"
                ],
                "restricted_fields": [
                    {
                        "field": "ssn",
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
                "resource": "http://localhost:8000/users",
                "allowed_methods": [
                    "GET",
                ],
                "restricted_fields": [
                    {
                        "field": "ssn",
                        "request": True,
                        "response": True
                    }
                ],
                "redacted_fields": [
                    {
                        "field": "ssn",
                        "filter": "age < 18"
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
                "resource": "http://localhost:8000/users",
                "allowed_methods": []
            }
        },
        {
            "rule": {
                "resource": "http://localhost:8000/users/[\\w]+",
                "allowed_methods": [
                    "GET"
                ],
                "restricted_fields": [
                    {
                        "field": "ssn",
                        "request": True,
                        "response": True
                    }
                ],
                "redacted_fields": [
                    {
                        "field": "firstname",
                        "filter": "age < 18"
                    },

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
                "resource": "http://localhost:8000/users",
                "allowed_methods": []
            }
        },
        {
            "rule": {
                "resource": "http://localhost:8000/users/[\\w]+",
                "allowed_methods": [
                    "GET"
                ],
                "restricted_fields": [
                    {
                        "field": "id",
                        "request": True,
                        "response": True
                    }
                ],
                "redacted_fields": [
                    {
                        "field": "ssn",
                        "filter": "age < 18"
                    },

                ],
                "access_policies": [
                    {
                        "description": "description of policy",
                        "filter": "age < 18"
                    }
                ]
            }
        }
    ]
}

COMPLEX_RULESET_SCOPE = {
    "scope": "all:restrict-redact-filter",
    "ruleset": [
        {
            "rule": {
                "resource": "http://localhost:8000/users/[\\w]+",
                "allowed_methods": [
                    '*'
                ],
                "restricted_fields": [
                    {
                        "field": "id",
                        "request": True,
                        "response": True
                    }
                ],
                "redacted_fields": [
                    {
                        "field": "ssn",
                        "filter": "*"
                    },
                    {
                        "field": "firstname",
                        "filter": "age < 21"
                    },
                    {
                        "field": "middlename",
                        "filter": "age < 21"
                    },
                    {
                        "field": "lastname",
                        "filter": "age < 21"
                    },
                    {
                        "field": "suffix",
                        "filter": "age < 21"
                    },
                    {
                        "field": "date_registered",
                        "filter": "age == 45"
                    }

                ],
                "access_policies": [
                    {
                        "description": "description of policy",
                        "filter": "age < 18"
                    }
                ]
            }
        }
    ]
}

ALL_SCOPES = [
    {
        'name': 'full-access-scope',
        'scope': FULL_ACCESS_SCOPE
    },
    {
        'name': 'read-only-scope',
        'scope': READ_ONLY_SCOPE
    },
    {
        'name': 'redaction-scope',
        'scope': REDACTION_SCOPE
    },
    {
        'name': 'redaction-access-policy-scope',
        'scope': REDACTION_ACCESS_POLICY_SCOPE
    },
    {
        'name': 'restriction-access-policy-scope',
        'scope': RESTRICTION_ACCESS_POLICY_SCOPE
    },
    {
        'name': 'complex-ruleset-scope',
        'scope': COMPLEX_RULESET_SCOPE
    }
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


@pytest.fixture(scope='session')
def scopes():
    return ALL_SCOPES


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
            role = Role(role=scope['scope']['scope'], description='a test role', rules=json.dumps(scope['scope']))
            db.session.add(role)
            db.session.commit()
    yield app
    postgres.stop_container()
