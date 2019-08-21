"""Simple Flask API"""

import os
from flask import Flask
from flask_migrate import Migrate
from strawman.db import db
from strawman.api import user_bp


class Config(object):
    """Application configuration object."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://dev_user:dev_password@localhost:5432/authservice_dev')


def create_app():
    """Create the Flask application and configure it."""

    app = Flask(__name__)
    app.config.from_object(Config())
    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(user_bp)

    return app
