"""
This module defines a Flask blueprint for user-related functionality.

The blueprint, named 'user', provides routes for managing user data,
including displaying users in a table, creating new users, editing
existing users, and assigning projects to users.

Blueprint Details:
- Blueprint Name: user
- URL Prefix: /user
- Decorators: admin_permissions (applied to all routes)

Routes:
- GET /user/ : Display users in a table
- GET /user/delete-confirmation/<int:user_id> : Display delete confirmation for a user
- DELETE /user/<int:user_id> : Remove a user
- GET/POST /user/create : Create a new user
- GET /user/<int:user_id>/edit : Render input fields to edit a user
- PUT /user/<int:user_id> : Update an existing user
- GET /user/<int:user_id>/row : Render a single user row
- GET /user/clear : Clear rendered content
- GET/PUT /user/assign-project : Assign a project to a user
- POST /user/project-action/ : Perform an action on a user's projects

"""

from flask import (
    Blueprint,
    render_template,
    request,
)
from app.db import get_projectdao, get_userdao
from app.auth import admin_permissions

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/")
@admin_permissions
def display_page():
    """Display users in a table."""
    users = get_userdao().fetch_user()
    return render_template("user/index.html", users=users)


@bp.route("/delete-confirmation/<int:user_id>")
@admin_permissions
def delete_confirmation_user(user_id):
    """Display users in a table."""
    return render_template("user/delete-confirmation.html", user_id=user_id)


@bp.delete("/<int:user_id>")
@admin_permissions
def remove_user(user_id):
    """Delete a user."""
    try:
        get_userdao().remove_user(user_id)
    except Exception as e:
        print("There was an error deleting user" + str(e))
    else:
        return "<tr>User Deleted</tr>"

    return None


@bp.route("/create", methods=["GET", "POST"])
@admin_permissions
def create_user():
    """Create a new user."""
    if request.method == "POST":
        user_info = {
            "email": request.form["user-email"],
            "firstname": request.form["user-firstname"],
            "lastname": request.form["user-lastname"],
            "role": request.form["user-role"],
            "password": request.form["user-password"],
        }
        try:
            user_id = get_userdao().create_user(user_info)[0]
        except Exception as e:
            print("There was an error creating user" + str(e))
        else:
            return render_template("user/row.html", user=user_info, user_id=user_id)

    return render_template("user/create.html")


@bp.get("/<int:user_id>/edit")
@admin_permissions
def user_input_fields(user_id):
    """Render input fields to edit a user."""
    user = get_userdao().fetch_user(user_id)[0]
    return render_template("user/edit.html", user=user, user_id=user_id)


@bp.put("/<int:user_id>")
@admin_permissions
def update_user(user_id):
    """Update an existing user."""
    user_info = {
        "email": request.form["user-email"],
        "firstname": request.form["user-firstname"],
        "lastname": request.form["user-lastname"],
        "role": request.form["user-role"],
        "password": request.form["user-password"],
    }

    try:
        get_userdao().update_user(user_info, user_id)
    except Exception as e:
        print("There was an error updating user: " + str(e))
    else:
        return render_template("user/row.html", user=user_info, user_id=user_id)

    return None


@bp.route("/<int:user_id>/row")
@admin_permissions
def render_datarow(user_id):
    """Render a single user row."""
    user = get_userdao().fetch_user(user_id)[0]
    return render_template("user/row.html", user=user, user_id=user_id)


@bp.route("/clear")
@admin_permissions
def clear_content():
    """Clear rendered content."""
    return ""


@bp.route("/assign-project", methods=["GET", "PUT"])
@admin_permissions
def assign_project():
    """Assign a project to a user."""
    users = get_userdao().fetch_user()

    if request.method == "PUT":
        action = request.form["action"]
        user_id = request.form["user-id"]
        project_list = request.form.getlist("projects")

        if action == "assign":
            for project_id in project_list:
                get_userdao().assign_project(user_id, project_id)
        elif action == "unassign":
            for project_id in project_list:
                get_userdao().unassign_project(user_id, project_id)

    return render_template("user/assign-project.html", users=users)


@bp.post("/project-action/")
@admin_permissions
def project_action():
    """Assign a project to a user."""
    user_id = request.form["user-id"]
    action = request.form["action"]
    user_projects = get_userdao().fetch_user_projects(user_id)
    projects = get_projectdao().fetch_projects()
    projects_to_remove = [item[0] for item in user_projects]
    filtered_projects = [
        project for project in projects if project[0] not in projects_to_remove
    ]

    return render_template(
        "user/project-action.html",
        projects=projects,
        user_projects=user_projects,
        action=action,
        filtered_projects=filtered_projects,
    )
