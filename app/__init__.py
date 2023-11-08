"""Main application module.

Creates and configures the Flask app instance.
Registers blueprints and assets.
"""
import os

from flask import Flask, redirect, url_for
from flask_assets import Bundle, Environment

from config import ProdConfig, DevConfig
from . import auth
from . import db
from . import project
from . import record
from . import user


def create_app():
    """Create and configure the Flask application."""
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.register_blueprint(auth.bp)

    app.register_blueprint(record.bp)

    app.register_blueprint(project.bp)

    app.register_blueprint(user.bp)

    db.init_app(app)

    if os.environ.get("FLASK_ENV") == "production":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)

    assets = Environment(app)
    css = Bundle("src/main.css", output="dist/main.css")
    js = Bundle("src/*.js", output="dist/main.js")
    assets.register("css", css)
    assets.register("js", js)
    css.build()
    js.build()

    @app.route("/")
    def root():
        return redirect(url_for("auth.login"))

    return app
