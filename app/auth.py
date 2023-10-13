"""
This module defines a Flask blueprint for managing user authentication and registration.

The blueprint, named 'auth', provides routes for registering new users, logging in registered users, and logging out users.

Blueprint Details:
- Blueprint Name: auth
- URL Prefix: /auth
- Decorators: admin_permissions (applied to register route)

Routes:
- GET/POST /auth/register : Register a new user account
- GET/POST /auth/login : Log in a registered user
- GET /auth/logout : Log out and clear user session
- POST /auth/email : Validate email format and existence

Helper Functions:
- is_valid_email : Assert that an email is valid
- is_logged_in : Check if a user is logged in
- login_required : Require login to access view
- admin_permissions : Require admin permissions to access view
- get_current_user : Get user object for currently logged in user
- load_logged_in_user : Set global user object before request

"""

import re
import functools

from flask import Blueprint, redirect, render_template, request, session, url_for, g
from werkzeug.security import check_password_hash
from app.db import get_userdao

bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_valid_email(email):
    """Assert that an email is valid."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def is_logged_in():
    """Check if a user is logged in."""
    return "user_id" in session


def login_required(view):
    """Require login to access view."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


def admin_permissions(view):
    """Require admin permissions to access view."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user_role != "admin" or g.user is None:
            return render_template("auth/permission-denied.html")

        return view(**kwargs)

    return wrapped_view


def get_current_user():
    """Get user object for currently logged in user."""
    user_id = session.get("user_id")
    if user_id is None:
        return None

    user = get_userdao().fetch_user(user_id)[0]
    return user


@bp.before_app_request
def load_logged_in_user():
    """Set global user object before request."""
    g.user = get_current_user()
    if g.user:
        g.user_role = g.user["role"]
    else:
        g.user_role = None


@bp.route("/register", methods=("GET", "POST"))
@admin_permissions
def register():
    """Register a new user account."""
    if request.method == "POST":
        email = request.form["email"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        password = request.form["password"]
        role = "creator"
        error = None

        if not is_valid_email(email):
            error = "Please enter a valid email!"

        if error is None:
            get_userdao().create_user(
                {
                    "email": email,
                    "firstname": firstname,
                    "lastname": lastname,
                    "password": password,
                    "role": role,
                }
            )
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if g.user is not None:
        return redirect(url_for("data.display_page"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_userdao().fetch_user_by_email(email)
        if user is None:
            return "Incorrect Username."
        elif not check_password_hash(user["password"], password=password):
            return "Incorrect Password."

        session.clear()
        session["user_id"] = user["user_id"]
        return redirect(url_for("data.display_page"))

    return render_template("auth/login.html", title="Login Page")


@bp.route("/logout")
def logout():
    """Log out and clear user session."""
    print("you logged out")
    session.clear()
    return redirect(url_for("auth.login"))


@bp.post("/email")
def validate_email():
    """Validate email format and existence."""
    email = request.form["user-email"]
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
