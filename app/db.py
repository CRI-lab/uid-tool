"""
This module contains functions for handling database connections and initializing the application.
"""
import os
import psycopg2
import psycopg2.extras
import click
from flask import current_app, g, Flask
from app.dao.DataDao import Data
from app.dao.ProjectDao import Project
from app.dao.UserDao import User


def get_db():
    """Returns a database connection object."""
    try:
        if "db" not in g:
            db_uri = os.getenv("DEV_DATABASE_URI") if os.environ.get("FLASK_ENV") == "development" else os.getenv("PROD_DATABASE_URI")
            g.db = psycopg2.connect(db_uri, cursor_factory=psycopg2.extras.DictCursor)
        return g.db
    except psycopg2.OperationalError as e:
        print("Error connecting to database: ", e)
    return g.db


def load_dao():
    """Load DAO objects."""
    g.data_dao = Data(get_db())


def get_datadao():
    """Get Data DAO objects"""
    g.data_dao = Data(get_db())
    return g.data_dao


def get_projectdao():
    """Get project DAO objects"""
    g.project_dao = Project(get_db())
    return g.project_dao


def get_userdao():
    """Get user DAO object"""
    g.user_dao = User(get_db())
    return g.user_dao


def close_db(_=None):
    """Close Db connection."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Initialize the database."""
    db = get_db()
    cursor = db.cursor()
    user_dao = get_userdao()

    try: 
        with current_app.open_resource("schema.sql") as file:
            sql = file.read()

        cursor.execute(sql)
        db.commit()

        users = [
            {
                "email": "test123@gmail.com",
                "firstname": "test",
                "lastname": "asdf",
                "role": "admin",
                "password": "asdf",
                "inactive": False
            },
            {
                "email": "asdf@gmail.com",
                "firstname": "test",
                "lastname": "asdf",
                "role": "creator",
                "password": "asdf",
                "inactive": False
            },
        ]

        for user in users:
            user_dao.create_user(user)

        project_ids = [1, 2, -1]
        for project_id in project_ids:
            user_dao.assign_project(1, project_id)
    except psycopg2.Error as e:
        print("Error adding data to database: ", e)
    except (FileNotFoundError, IOError) as e:
        print("Error reading schema.sql file: ", e)


def init_app(app: Flask):
    """Initialize the application."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.before_request(load_dao)


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new table"""
    init_db()
    click.echo("Initialized the database")
