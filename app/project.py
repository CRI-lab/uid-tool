from flask import Blueprint, redirect, render_template, request, session, url_for
from app.db import get_db
from datetime import datetime

bp = Blueprint("project", __name__, url_prefix="/project")


@bp.route("/")
def display_page():
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


@bp.route("/update")
def update_page():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM project")
    projects = cursor.fetchall()
    return render_template("project/update.html", projects=projects)


@bp.route("/project_name")
def project_name():
    db = get_db()
    cursor = db.cursor()
    project_name = request.form["project-name"]
    cursor.execute("SELECT * FROM project WHERE data_name=%s", (project_name,))
    exists = cursor.fetchone()

    return render_template("project/validation.html", exists=exists)


@bp.route("/create", methods=["GET", "POST"])
def create_project():
    db = get_db()
    cursor = db.cursor()
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":
        project_name = request.method["project-name"]
        project_code = request.method["project-code"]
        finished = False if request.form.get("finished") is None else True
        # Will return the empty row inputs
        cursor.execute(
            "INSERT INTO project VALUES (%s, %s, %s, %s)",
            (created_date, project_name, project_code, finished),
        )
        db.commit()
        cursor.execute("SELECT * from project WHERE project_name=%s", (project_name,))
        project = cursor.fetchone()
        return render_template("project/row.html", project=project)

    return render_template("project/create.html", created_date=created_date)


@bp.get("/<int:project_id>/edit")
def project_input_fields(project_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM project WHERE project_id=%s", (project_id,))
    project = cursor.fetchone()
    return render_template("project/edit.html", project=project, project_id=project_id)


@bp.get("/<int:project_id>")
def fetch_project(project_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM project WHERE project_id=%s", (project_id,))
    project = cursor.fetchone()[0]
    return project


@bp.put("/<int:project_id>")
def update_project(project_id):
    db = get_db()
    cursor = db.cursor()
    project_name = request.form["project_name"]
    finished = False if request.form.get("finished") is None else True
    try:
        cursor.execute(
            "UPDATE project SET project_name=%s, finished=%s WHERE project_id=%s",
            (project_name, finished, project_id),
        )
        db.commit()
    except Exception as e:
        print("There was an error updated data: " + e)
    else:
        cursor.execute("SELECT * FROM project WHERE project_id=%s", (project_id,))
        data = cursor.fetchone()
        return render_template("project/row.html", data=data)


@bp.delete("/<int:project_id>")
def delete_project(project_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM project WHERE project_id=%d", (project_id,))
        db.commit()
    except Exception as e:
        print("There was an error deleting data: " + e)
    else:
        return "<tr>Project deleted</tr>"


@bp.route("/<int:project_id>/row")
def render_datarow(project_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM project WHERE project_id=%s", (project_id,))
    project = cursor.fetchone()
    return render_template("project/row.html", project=project)


@bp.route("/clear")
def clear_content():
    return ""


# @bp.route("/create")
# def create():


# @bp.route("/update/<int:project_id>")
# def update(project_id):
