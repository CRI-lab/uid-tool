import os
import psycopg2
import psycopg2.extras
import click
from flask import current_app, g, Flask
from werkzeug.security import generate_password_hash, check_password_hash
from app.dao.DataDao import Data
from app.dao.ProjectDao import Project
from app.dao.UserDao import User


def get_db():
    if "db" not in g:
        g.db = (
            psycopg2.connect(
                os.getenv("DEV_DATABASE_URI"), cursor_factory=psycopg2.extras.DictCursor
            )
            if os.environ.get("FLASK_ENV") == "development"
            else psycopg2.connect(
                os.getenv("PROD_DATABASE_URI"),
                cursor_factory=psycopg2.extras.DictCursor,
            )
        )
        return g.db
    return g.db


def load_dao():
    g.data_dao = Data(get_db())


def get_datadao():
    g.data_dao = Data(get_db())
    return g.data_dao


def get_projectdao():
    g.project_dao = Project(get_db())
    return g.project_dao


def get_userdao():
    g.user_dao = User(get_db())
    return g.user_dao


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    cur = db.cursor()
    userdao = get_userdao()
    with current_app.open_resource("schema.sql") as f:
        sql = f.read()
    cur.execute(sql)
    db.commit()

    user1 = {
        "email": "test123@gmail.com",
        "firstname": "test",
        "lastname": "asdf",
        "role": "admin",
        "password": "asdf",
    }
    user2 = {
        "email": "asdf@gmail.com",
        "firstname": "test",
        "lastname": "asdf",
        "role": "creator",
        "password": "asdf",
    }

    userdao.create_user(user1)
    userdao.create_user(user2)

    userdao.assign_project(1, 1)
    userdao.assign_project(1, 2)
    userdao.assign_project(1, -1)


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.before_request(load_dao)


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new table"""
    init_db()
    click.echo("Initialized the database")
