"""Simple Flask API"""

from flask import Flask
from flask_migrate import Migrate
from strawman.db import db


def create_app():
    """Create the Flask application and configure it."""

    app = Flask(__name__)
    db.init_app(app)
    migrate = Migrate(app, db)

    return app
