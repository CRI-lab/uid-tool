from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.db import get_db
from datetime import datetime

bp = Blueprint("data", __name__, url_prefix="/data")


@bp.route("/", methods=["GET", "POST"])
def display():
    return render_template("data/index.html")


@bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        user_id = session["user_id"]
        data_name = request.form["data-name"]
        project1 = request.form["project1"]
        project2 = request.form["project2"]
        location = request.form["file-location"]
        created_date = datetime.now()
        db_created = created_date.strftime("%Y-%m-%d %H:%M:%S")
        coastal6 = False if request.form.get("coastal6") is None else True

        db = get_db()
        cursor = db.cursor()

        try:
            if project2 is not None and coastal6 is not None:
                cursor.execute(
                    "SELECT project_id, code FROM project WHERE project_name=%s OR project_name=%s",
                    (project1, project2),
                )
                [project1, project1_code] = cursor.fetchone()
                project2 = 1

                uid = f"CRCYYMMDD001{project1_code}XX"

                cursor.execute(
                    "INSERT INTO data (creator_id, project_id_1, project_id_2, created, data_name, file_location, coastal6, uid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING data_id;",
                    (
                        user_id,
                        project1,
                        project2,
                        db_created,
                        data_name,
                        location,
                        coastal6,
                        uid,
                    ),
                )
                db.commit()
                data_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO coastal6 (data_id) VALUES (%s)", (data_id,))
                db.commit()
        except Exception as error:
            print(project1)
            print("There was an error in inserting data to db:", error)
        else:
            return redirect(url_for("data.create"))

    return render_template("data/create.html")
