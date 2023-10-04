from flask import (
    Blueprint,
    render_template,
    request,
)
from app.db import  get_projectdao, get_userdao

bp = Blueprint("user", __name__, url_prefix="/user")

@bp.route("/")
def display_page():
    users = get_userdao().fetch_user()
    return render_template('user/index.html', users=users)

@bp.route("/delete-confirmation/<int:user_id>")
def  delete_confirmation_user(user_id):
    return render_template("user/delete-confirmation.html", user_id=user_id)

@bp.delete("/<int:user_id>")
def remove_user(user_id):
    try:
        get_userdao().remove_user(user_id)
    except Exception as e:
        print("There was an error deleting user" + str(e))
    else:
        return "<tr>User Deleted</tr>"

@bp.route("/create", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        user_info = dict()
        user_info["email"] = request.form["user-email"]
        user_info["firstname"] = request.form["user-firstname"]
        user_info["lastname"] = request.form["user-lastname"]
        user_info["role"] = request.form["user-role"]
        user_info["password"] = request.form["user-password"]
        try:
            user_id = get_userdao().create_user(user_info)[0]
        except:
            print("There was an creating user")
        else:
            return render_template("user/row.html", user=user_info, user_id=user_id)

    return render_template("user/create.html")

@bp.get("/<int:user_id>/edit")
def user_input_fields(user_id):
    user = get_userdao().fetch_user(user_id)[0] 
    return render_template("user/edit.html", user=user, user_id=user_id)

@bp.put("/<int:user_id>")
def update_project(user_id):
    user_info = dict()
    user_info["email"] = request.form["user-email"]
    user_info["firstname"] = request.form["user-firstname"]
    user_info["lastname"] = request.form["user-lastname"]
    user_info["role"] = request.form["user-role"]
    try:
        get_userdao().update_user(user_info, user_id)
    except Exception as e:
        print("There was an error updating user: " + e)
    else:
        return render_template("user/row.html", user=user_info, user_id=user_id)

@bp.route("/<int:user_id>/row")
def render_datarow(user_id):
    user = get_userdao().fetch_user(user_id)[0]
    return render_template("user/row.html", user=user, user_id=user_id)


@bp.route("/clear")
def clear_content():
    return ""

@bp.route("/assign-project", methods=["GET", "POST", "DELETE"])
def assign_project():
    users = get_userdao().fetch_user()
    if request.method == "POST":
        action = request.form["action"]
        if action == "assign":
            user_id = request.form["user-id"]
            project_list = request.form.getlist('projects')
            for project_id in project_list:
                get_userdao().assign_project(user_id, project_id)
    
    if request.method == "DELETE":
        #TODO Implement in Dao
        get_userdao().unassign_project(project_id)

    return render_template("user/assign-project.html", users=users)

@bp.post("/project-action/")
def project_action():
    user_id = request.form["user-id"]
    action = request.form["action"]
    user_projects = get_userdao().fetch_user_projects(user_id)
    projects = get_projectdao().fetch_projects()
    projects_to_remove = [item[0] for item in user_projects]
    filtered_projects = [project for project in projects if project[0] not in projects_to_remove]
    print(filtered_projects)

    return render_template("user/project-action.html", projects=projects, user_projects=user_projects, action=action, filtered_projects=filtered_projects)