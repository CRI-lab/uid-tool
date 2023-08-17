import os

from flask import Flask, redirect, session, url_for
from flask_assets import Bundle, Environment


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )
    app.secret_key = "test123"
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None"

    from . import auth

    app.register_blueprint(auth.bp)

    from . import data

    app.register_blueprint(data.bp)

    from . import db

    db.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    assets = Environment(app)
    css = Bundle("src/main.css", output="dist/main.css")
    js = Bundle("src/*.js", output="dist/main.js")
    assets.register("css", css)
    assets.register("js", js)
    css.build()
    js.build()

    @app.route("/")
    def homepage():
        return redirect(url_for("auth.login"))

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    return app
