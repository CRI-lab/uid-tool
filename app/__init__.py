import os

from flask import Flask, redirect, url_for, request
from flask_assets import Bundle, Environment
from config import ProdConfig, DevConfig


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import data

    app.register_blueprint(data.bp)

    from . import project

    app.register_blueprint(project.bp)

    from . import user

    app.register_blueprint(user.bp)

    from . import db

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
