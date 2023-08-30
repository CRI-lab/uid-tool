from flask import Blueprint, redirect, render_template, request, session, url_for
from app.db import get_db
from datetime import datetime

bp = Blueprint("project", __name__, url_prefix="/project")


@bp.route("/")
def display():
    """
    Display projects in a table

    Returns:
        string: html of the page that dispalys the projects
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM project")
    projects = cursor.fetchall()
    return render_template("project/index.html", projects=projects)


# @bp.route("/create")
# def create():


# @bp.route("/update/<int:project_id>")
# def update(project_id):


# @bp.route("/delete/<int:project_id>")
# def delete(project_id):
