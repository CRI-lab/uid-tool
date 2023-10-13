"""Project blueprint to manage project CRUD operations"""
from datetime import datetime
from flask import Blueprint, render_template, request
from app.db import get_projectdao
from app.auth import admin_permissions

bp = Blueprint("project", __name__, url_prefix="/project")


@bp.route("/")
def display_page():
    """Display projects in a table"""
    projects = get_projectdao().fetch_projects()
    return render_template("project/index.html", projects=projects)


@bp.route("/update")
@admin_permissions
def update_page():
    """Display page for updating projects."""
    projects = get_projectdao().fetch_projects()
    return render_template("project/update.html", projects=projects)


@bp.post("/project_name")
def project_name():
    """Validate if a project name exists."""
    name = request.form["project-name"]
    exists = get_projectdao().fetch_project_by_name(name)

    return render_template("project/validation.html", exists=exists)


@bp.route("/create", methods=["GET", "POST"])
@admin_permissions
def create_project():
    """Create a new project."""
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if request.method == "POST":
        project_info = {
            "project_name": request.form["project-name"],
            "code": request.form["project-code"].upper(),
            "finished": bool(request.form.get("finished")),
            "created": created_date,
        }
        project_info["project_id"] = get_projectdao().create_project(project_info)
        return render_template("project/row.html", project=project_info)

    return render_template("project/create.html", created_date=created_date)


@bp.get("/<int:project_id>/edit")
@admin_permissions
def project_input_fields(project_id):
    """Render input fields to edit a project."""
    project = get_projectdao().fetch_project_by_id(project_id)
    return render_template("project/edit.html", project=project, project_id=project_id)


@bp.get("/<int:project_id>")
def fetch_project(project_id):
    """Fetch project information."""
    project = get_projectdao().fetch_project_by_id(project_id)
    return project


@bp.put("/<int:project_id>")
@admin_permissions
def update_project(project_id):
    """Update an existing project."""
    project_info = {}
    project_info["project_name"] = request.form["project_name"]
    project_info["finished"] = bool(request.form.get("finished"))
    get_projectdao().update_project(project_info, project_id)
    project = get_projectdao().fetch_project_by_id(project_id)
    return render_template("project/row.html", project=project)


@bp.delete("/<int:project_id>")
@admin_permissions
def delete_project(project_id):
    """Delete a project."""
    get_projectdao().remove_project(project_id)
    return "<tr>Project deleted</tr>"


@bp.route("/<int:project_id>/row")
def render_datarow(project_id):
    """Render a single project row"""
    project = get_projectdao().fetch_project_by_id(project_id)
    return render_template("project/row.html", project=project)


@bp.route("/clear")
def clear_content():
    """Clear rendered content."""
    return ""
