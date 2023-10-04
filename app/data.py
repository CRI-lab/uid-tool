import io
import csv

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    url_for,
    send_file,
    Response,
)
from app.db import get_datadao, get_projectdao, get_userdao
from app.auth import login_required
from datetime import datetime

bp = Blueprint("data", __name__, url_prefix="/data")

@bp.route("/")
def display_page():
    data_entries = get_datadao().fetch_data_table(filters={})
    session["data"] = data_entries
    projects = get_projectdao().fetch_projects()
    emails = get_userdao().fetch_user_emails()
    emails = [email[0] for email in emails]

    return render_template("data/index.html", data_entries=data_entries, projects=projects, emails=emails)


@bp.post("/data_name")
def check_data_exists():
    data_name = request.form["data-name"]
    exists = get_datadao().fetch_data_by_name(data_name)

    return render_template("data/validation.html", exists=exists)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_data():
    user_id = session["user_id"]
    project_list = get_projectdao().fetch_project_by_user(user_id)

    if request.method == "POST":
        data_info = dict()
        data_info["user_id"] = user_id
        data_info["data_name"] = request.form["data-name"]
        project1_id = data_info["project1_id"] = request.form["project1-id"]
        project2_id = data_info["project2_id"] = request.form["project2-id"]
        data_info["data_description"] = request.form["data-description"]
        data_info["invenio"] = False if request.form.get("invenio") is None else True
        data_info["data_location_type"] = request.form["data-location-type"]
        data_info["data_location"] = request.form["data-location"]
        created_date = datetime.now()
        data_info["db_created"] = created_date.strftime("%Y-%m-%d %H:%M:%S")
        id_date = created_date.strftime("%Y%m%d")


        try:
            if project2_id != "-1" and project1_id != project2_id:
                project1_code, project2_code = get_projectdao().get_projects_from_id(project1_id, project2_id)
            else:
                project1_code, project2_code = get_projectdao().get_projects_from_id(project1_id = project1_id)
                data_info["project2_id"] = "-1"

            # get id from last entry
            data_id = get_datadao().fetch_last_data_id()
            if data_id is None:
                data_id = str(1).zfill(3)
            else:
                data_id = str(data_id[0] + 1).zfill(3)
            uid = f"CRC{id_date}{data_id}{project1_code}{project2_code}"
            data_info["uid"] = uid
            
            get_datadao().create_data(data_info=data_info)

        except Exception as error:
            print("There was an error in inserting data to db:", error)
        else:
            download_url = url_for("data.download_readme", data_id=data_id)
            data_page_url = url_for("data.display_page")
            return render_template(
                "data/download.html",
                download_url=download_url,
                data_page_url=data_page_url,
            )
    return render_template("data/create.html", projects=project_list)


@bp.get("/download/<int:data_id>")
@login_required
def download_readme(data_id):
    data = get_datadao().fetch_data_by_id(data_id)
    data_info = ""
    for key, value in data.items():
       data_info += f"{key}: {value}\n" 
    buffer = io.BytesIO()
    buffer.write(data_info.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="README.txt",
        mimetype="text/plain",
    )


@bp.route("/update", methods=["GET", "POST"])
@login_required
def update_page():
    user_id = session["user_id"]
    #TODO Need to include project association
    data_entries = get_datadao().fetch_project_data(user_id)
    return render_template(
        "data/update.html", data_entries=data_entries)


@bp.get("/<int:data_id>")
def fetch_data(data_id):
    data = get_datadao().fetch_data_by_id(data_id)
    return data

@bp.put("/<int:data_id>")
@login_required
def update_data(data_id):
    data_info = dict()
    data_info['data_name'] = request.form['data-name']
    data_info['data_description'] = request.form['data-description']
    data_info['data_location_type'] = request.form['data-location-type']
    data_info['data_location'] = request.form['data-location']
    data_info['invenio'] = False if request.form.get("invenio") is None else True
    try:
        get_datadao().update_data(data_info=data_info, data_id=data_id)
    except Exception as e:
        print("There was an error updated data: " + e)
    else:
        data = get_datadao().fetch_data_by_id(id=data_id)
        return render_template("data/row.html", data=data)


@bp.delete("/<int:data_id>")
@login_required
def remove_data(data_id):
    try:
       get_datadao().remove_data(data_id) 
    except Exception as e:
        print("There was an error deleting data: " + e)
    else:
        return "<tr>Delete Successful</tr>"


@bp.route("/<int:data_id>/row")
@login_required
def render_datarow(data_id):
    data = get_datadao().fetch_data_by_id(data_id)
    return render_template("data/row.html", data=data)


@bp.get("/<int:data_id>/edit")
@login_required
def edit_data(data_id):
    data = get_datadao().fetch_data_by_id(data_id)
    return render_template("data/edit2.html", data=data)


@bp.post("/location-type")
@login_required
def data_location_field():
    location = request.form["data-location-type"]
    return render_template("data/location.html", location=location)

@bp.post("/filter")
def filter_data_table():
    filters = dict()
    filters["data_name_match"] = request.form["data-name"]
    filters["from_date"] = request.form["from-date"]
    filters["to_date"] =request.form["to-date"]
    filters["email"] = request.form["email"]
    filters["data_location_type"] = request.form["data-location-type"]
    filters["invenio"] = request.form["invenio"]  
    filters["project"] = request.form["project"]
    filters["uid"] = request.form["uid"]
    
    session["data"] = data_entries = get_datadao().fetch_data_table(filters)

    return render_template("data/table-body.html", data_entries=data_entries)
    
@bp.get("/download-table-csv")
def download_table_csv():
    data = session.get('data', {})
    output = get_datadao().write_to_csv(data)

    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=output.csv'}
    )

@bp.get("/delete-confirmation/<int:data_id>")
def delete_confirmation(data_id):
    return render_template("data/delete-confirmation.html", data_id=data_id)