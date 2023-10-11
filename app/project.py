from flask import Blueprint, redirect, render_template, request, session, url_for
from datetime import datetime
from app.db import get_projectdao

bp = Blueprint("project", __name__, url_prefix="/project")


@bp.route("/")
def display_page():
    """
    Display projects in a table

    Returns:
        string: html of the page that dispalys the projects
    """
    projects = get_projectdao().fetch_projects()
    return render_template("project/index.html", projects=projects)


@bp.route("/update")
def update_page():
    projects = get_projectdao().fetch_projects()
    return render_template("project/update.html", projects=projects)


@bp.post("/project_name")
def project_name():
    project_name = request.form["project-name"]
    try:
        project = get_projectdao().fetch_project_by_name(project_name)
    except:
        print("There was a erorr getting project name")
    else:
        exists = False if project is None else True

    return render_template("project/validation.html", exists=exists)


@bp.route("/create", methods=["GET", "POST"])
def create_project():
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if request.method == "POST":
        project_info = dict()
        project_info["project_name"] = request.form["project-name"]
        project_info["code"] = request.form["project-code"].upper()
        project_info["finished"] = (
            False if request.form.get("finished") is None else True
        )
        project_info["created"] = created_date
        # Will return the empty row inputs
        get_projectdao().create_project(project_info)
        return render_template("project/row.html", project=project_info)

    return render_template("project/create.html", created_date=created_date)


@bp.get("/<int:project_id>/edit")
def project_input_fields(project_id):
    project = get_projectdao().fetch_project_by_id(project_id)
    return render_template("project/edit.html", project=project, project_id=project_id)


@bp.get("/<int:project_id>")
def fetch_project(project_id):
    project = get_projectdao().fetch_project_by_id(project_id)
    return project


@bp.put("/<int:project_id>")
def update_project(project_id):
    project_info = dict()
    project_info["project_name"] = request.form["project_name"]
    project_info["finished"] = False if request.form.get("finished") is None else True
    try:
        get_projectdao().update_project(project_info, project_id)
    except Exception as e:
        print("There was an error updated data: " + e)
    else:
        project = get_projectdao().fetch_project_by_id(project_id)
        return render_template("project/row.html", project=project)


@bp.delete("/<int:project_id>")
def delete_project(project_id):
    try:
        get_projectdao().remove_project(project_id)
    except Exception as e:
        print("There was an error deleting data: " + str(e))
    else:
        return "<tr>Project deleted</tr>"


@bp.route("/<int:project_id>/row")
def render_datarow(project_id):
    project = get_projectdao().fetch_project_by_id(project_id)
    return render_template("project/row.html", project=project)


@bp.route("/clear")
def clear_content():
    return ""
