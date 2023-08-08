import re

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        email = request.form["email"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()

        try:
            print("uploading to db")
            cursor.execute(
                "INSERT INTO users (email, firstname, lastname, password) VALUES (%s, %s, %s, %s)",
                (email, firstname, lastname, generate_password_hash(password)),
            )
            db.commit()
        except db.IntegrityError:
            print(f"Error registering user. Please try again later.")
        else:
            print("upload successful")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor = get_db().cursor()

    return render_template("auth/login.html")


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


@bp.post("/email")
def validate_email():
    email = request.form["email"]
    cursor = get_db().cursor()
    if email and is_valid_email(email):
        cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
        exists = cursor.fetchone()
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
