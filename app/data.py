from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.db import get_db
from datetime import datetime

bp = Blueprint("data", __name__, url_prefix="/data")


@bp.route("/")
def display():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT data_name, u.firstname, u.lastname, d.created, file_location, coastal6, u.email, p1.project_name as project1_name, p2.project_name as project2_name, uid"
        " FROM public.data d JOIN public.users u on d.creator_id=u.user_id"
        " JOIN project p1 ON d.project_id_1=p1.project_id JOIN project p2 on d.project_id_2=p2.project_id"
        " ORDER BY d.created DESC"
    )
    data_entries = cursor.fetchall()
    return render_template("data/index.html", data_entries=data_entries)


@bp.post("/data_name")
def check_data_exists():
    db = get_db()
    cursor = db.cursor()
    data_name = request.form["data-name"]
    cursor.execute("SELECT * FROM data where data_name=%s", (data_name,))
    exists = cursor.fetchone()

    return render_template("data/validation.html", exists=exists)


@bp.route("/create", methods=["GET", "POST"])
def create():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM project")
    project_list = cursor.fetchall()

    if request.method == "POST":
        user_id = session["user_id"]
        data_name = request.form["data-name"]
        project1 = request.form["project1"]
        project2 = request.form["project2"]
        location = request.form["file-location"]
        created_date = datetime.now()
        db_created = created_date.strftime("%Y-%m-%d %H:%M:%S")
        id_date = created_date.strftime("%Y%m%d")
        coastal6 = False if request.form.get("coastal6") is None else True

        try:
            if project2 != -1 and project1 is not project2:
                cursor.execute(
                    "SELECT code FROM project WHERE project_id=%s OR project_id=%s ",
                    (project1, project2),
                )
                [[project1_code], [project2_code]] = cursor.fetchall()
            elif project1 == project2:
                cursor.execute(
                    "SELECT code FROM project WHERE project_id=%s",
                    (project1),
                )
                [project1_code] = cursor.fetchone()
                project2_code = "XX"
                project2 = -1

            # get id from last entry
            cursor.execute(
                "SELECT data_id FROM data ORDER BY data_id DESC LIMIT 1",
            )
            data_id = cursor.fetchone()
            if data_id is None:
                data_id = str(1).zfill(3)
            else:
                data_id = str(data_id[0] + 1).zfill(3)
            uid = f"CRC{id_date}{data_id}{project1_code}{project2_code}"

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
            print("There was an error in inserting data to db:", error)
        else:
            return redirect(url_for("data.create"))
    return render_template("data/create.html", projects=project_list)


@bp.route("/update", methods=["GET", "POST"])
def update():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT data_id, data_name, u.firstname, u.lastname, d.created, file_location, coastal6, u.email, p1.project_name as project1_name, p2.project_name as project2_name, uid"
        " FROM public.data d JOIN public.users u on d.creator_id=u.user_id"
        " JOIN project p1 ON d.project_id_1=p1.project_id JOIN project p2 on d.project_id_2=p2.project_id"
        " ORDER BY d.created DESC"
    )
    data_entries = cursor.fetchall()
    cursor.execute("SELECT * FROM project")
    project_list = cursor.fetchall()
    return render_template(
        "data/update.html", data_entries=data_entries, projects=project_list
    )


@bp.route("/<int:data_id>", methods=["GET", "PUT", "DELETE"])
def handle_data(data_id):
    db = get_db()
    cursor = db.cursor()
    if request.method == "GET":
        cursor.execute(
            "SELECT data_id, data_name, u.firstname, u.lastname, d.created, file_location, coastal6, u.email, p1.project_name as project1_name, p2.project_name as project2_name, uid"
            " FROM public.data d JOIN public.users u on d.creator_id=u.user_id"
            " JOIN project p1 ON d.project_id_1=p1.project_id JOIN project p2 on d.project_id_2=p2.project_id"
            " WHERE data_id=%s",
            (data_id,),
        )
        data = cursor.fetchone()
        return data
    elif request.method == "PUT":
        data_name = request.form["data_name"]
        location = request.form["data_location"]
        coastal6 = False if request.form.get("coastal6") is None else True
        try:
            cursor.execute(
                "UPDATE data"
                " SET data_name=%s, file_location=%s, coastal6=%s"
                " WHERE data_id=%s",
                (data_name, location, coastal6, data_id),
            )
            db.commit()
        except Exception as e:
            print("There was an error updated data: " + e)
        else:
            cursor.execute(
                "SELECT data_id, data_name, u.firstname, u.lastname, d.created, file_location, coastal6, u.email, p1.project_name as project1_name, p2.project_name as project2_name, uid"
                " FROM public.data d JOIN public.users u on d.creator_id=u.user_id"
                " JOIN project p1 ON d.project_id_1=p1.project_id JOIN project p2 on d.project_id_2=p2.project_id"
                " WHERE data_id=%s",
                (data_id,),
            )
            data = cursor.fetchone()
            return render_template("data/row.html", data=data)
    elif request.method == "DELETE":
        try:
            cursor.execute("DELETE FROM data WHERE data_id=%s", (data_id,))
            db.commit()
        except Exception as e:
            print("There was an error deleting data: " + e)
        else:
            return "<td>Delete Successful</td>"
    return "Invalid Operation"


@bp.route("/<int:data_id>/row")
def render_datarow(data_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT data_id, data_name, u.firstname, u.lastname, d.created, file_location, coastal6, u.email, p1.project_name as project1_name, p2.project_name as project2_name, uid"
        " FROM public.data d JOIN public.users u on d.creator_id=u.user_id"
        " JOIN project p1 ON d.project_id_1=p1.project_id JOIN project p2 on d.project_id_2=p2.project_id"
        " WHERE data_id=%s",
        (data_id,),
    )
    data = cursor.fetchone()
    return render_template("data/row.html", data=data)


@bp.get("/<int:data_id>/edit")
def edit_data(data_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT data_id, data_name, u.firstname, u.lastname, d.created, file_location, coastal6, u.email, p1.project_name as project1_name, p2.project_name as project2_name, uid"
        " FROM public.data d JOIN public.users u on d.creator_id=u.user_id"
        " JOIN project p1 ON d.project_id_1=p1.project_id JOIN project p2 on d.project_id_2=p2.project_id"
        " WHERE data_id=%s",
        (data_id,),
    )
    data = cursor.fetchone()
    data_id = data["data_id"]
    return render_template("data/edit.html", data=data, data_id=data_id)
