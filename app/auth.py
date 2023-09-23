import re
import functools

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
    g
)
from werkzeug.security import check_password_hash
from app.db import get_userdao

bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def is_logged_in():
    return "user_id" in session

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_userdao().fetch_user_by_id(user_id)

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        user_info = dict()
        user_info["email"] = request.form["email"]
        user_info["firstname"] = request.form["firstname"]
        user_info["lastname"] = request.form["lastname"]
        user_info["password"] = request.form["password"]
        error = None

        if not is_valid_email(user_info["email"]):
            error = "Please enter a valid email!"

        if error is None:
            try:
                get_userdao().create_user()
            except Exception as e:
                print("There was an error in registering user:", e)
                error = "Error registering user."
                return render_template("auth/error.html")
            else:
                return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        error = None
        user = get_userdao().fetch_user_by_email(email) 

        if user is None:
            error = "Incorrect Username."
        elif not check_password_hash(user["password"], password=password):
            error = "Incorrect Password."

        if error is None:
            session.clear()
            session["user_id"] = user["user_id"]
            return redirect(url_for("data.display_page"))
        return error

    return render_template("auth/login.html", title="Login Page")


@bp.route("/logout")
def logout():
    print("you logged out")
    session.clear()
    return redirect(url_for("auth.login"))


@bp.post("/email")
def validate_email():
    email = request.form["email"]
    if email and is_valid_email(email):
       exists = get_userdao().fetch_user_by_email(email)
    else:
        return render_template(
            "auth/validation.html",
            email=email,
            email_is_valid=False,
            email_exists=False,
        )

    if exists:
        return render_template(
            "auth/validation.html",
            email=email,
            email_is_valid=False,
            email_exists=True,
        )

    return (
        render_template(
            "auth/validation.html", email=email, email_is_valid=True, email_exists=False
        ),
        200,
    )
