"""Config file for Flask."""
from os import environ, path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Base config."""

    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME")
    SESSION_COOKIE_SECURE = True
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"


class ProdConfig(Config):
    """Production config."""

    FLASK_ENV = "production"
    DEBUG = False
    DATABSE_URI = environ.get("PROD_DATABASE_URI")


class DevConfig(Config):
    """Development config."""

    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True
    DATABSE_URI = environ.get("DEV_DATABASE_URI")
