"""Test Fixtures"""

import pytest
from time import sleep
from flask_migrate import upgrade

from strawman import create_app
from strawman.utilities import PostgreSQLContainer


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
        'postgres_database': '',
        'postgres_port': 5433,
        'postgres_image': 'postgres:11.4',
        'container_name': 'postgres_auth_strawman_test'
    }

    app = create_app()
    postgres = PostgreSQLContainer(DOCKER_CONFIGURATION)
    postgres.start_container()
    upgraded = False

    while not upgrade:
        try:
            with app.app_context():
                upgrade()
                upgraded = True
        except Exception as e:
            sleep(1)
    yield app
    postgres.stop_container()
