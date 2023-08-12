from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.db import get_db
from datetime import datetime

bp = Blueprint("data", __name__, url_prefix="/data")


@bp.route("/", methods=["GET", "POST"])
def display():
    return render_template("data/index.html")


@bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        user_id = 1
        data_name = request.form["data-name"]
        project1 = 1
        project2 = 1
        location = request.form["file-location"]
        coastal6 = bool(request.form["coastal6"])
        created_date = datetime.now().strftime("%Y-%m-%m %H:%M:%S")

        db = get_db()
        cursor = db.cursor()

        try:
            if project2 is not None and coastal6 is not None:
                cursor.execute()
                cursor.execute(
                    "INSERT INTO data (creator_id, project_id_1, project_id_2, created, data_name, file_location, coastal6) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (
                        user_id,
                        project1,
                        project2,
                        created_date,
                        data_name,
                        location,
                        coastal6,
                    ),
                )
                data_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO coastal6 (data_id) VALUES (%s)")
                db.commit()
        except Exception as error:
            print("There was an error in inserting data to db:", error)
        else:
            return redirect(url_for("data.create"))

    return render_template("data/create.html")
