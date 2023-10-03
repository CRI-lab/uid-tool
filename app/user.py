from flask import (
    Blueprint,
    render_template,
    request,
)
from app.db import  get_userdao

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