import os
import psycopg2
import psycopg2.extras
import click
from flask import current_app, g, Flask
from app.dao.DataDao import Data 
from app.dao.ProjectDao import Project
from app.dao.UserDao import User

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            os.getenv("DATABASE_URL"), cursor_factory=psycopg2.extras.DictCursor
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
    with current_app.open_resource("schema.sql") as f:
        sql = f.read()
    cur.execute(sql)
    db.commit()


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.before_request(load_dao)


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new table"""
    init_db()
    click.echo("Initialized the database")
