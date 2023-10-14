"""
This module defines a Flask blueprint for managing data-related functionality.

The blueprint, named 'data', provides routes for displaying data in a table,
creating new data entries, updating existing data entries, and deleting data entries.

Blueprint Details:
- Blueprint Name: data
- URL Prefix: /data
- Decorators: login_required (applied to all routes)

Routes:
- GET /data/ : Display data entries in a table
- POST /data/data_name : Check if data with a given name already exists
- GET/POST /data/create : Create a new data entry
- GET /data/download/<int:data_id> : Download the README file for a data entry
- GET/POST /data/update : Update a data entry
- DELETE /data/<int:data_id> : Remove a data entry
- GET /data/<int:data_id> : Fetch a data entry
- GET /data/<int:data_id>/row : Render a single data row
- GET /data/<int:data_id>/edit : Render input fields to edit a data entry
- POST /data/location-type : Fetch data by location type
- POST /data/filter : Filter the data table
- GET /data/download-table-csv : Download the data table as a CSV
- GET /data/delete-confirmation/<int:data_id> : Display delete confirmation for a data entry

"""
import io
from datetime import datetime

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

bp = Blueprint("data", __name__, url_prefix="/data")


@bp.route("/")
def display_page():
    """Display data entries in a table."""
    data_entries = get_datadao().fetch_data_table(filters={})
    session["data"] = data_entries
    projects = get_projectdao().fetch_projects()
    emails = get_userdao().fetch_user_emails()
    emails = [email[0] for email in emails]

    return render_template(
        "data/index.html", data_entries=data_entries, projects=projects, emails=emails
    )


@bp.post("/data_name")
def check_data_exists():
    """Check if data with a given name already exists."""
    data_name = request.form["data-name"]
    exists = get_datadao().fetch_data_by_name(data_name)

    return render_template("data/validation.html", exists=exists)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_data():
    """Create a new data entry in the database."""
    user_id = session["user_id"]
    project_list = get_projectdao().fetch_project_by_user(user_id)

    if request.method == "POST":
        data_info = {
            "user_id": user_id,
            "data_name": request.form["data-name"],
            "project1_id": request.form["project1-id"],
            "project2_id": request.form["project2-id"],
            "data_description": request.form["data-description"],
            "invenio": request.form.get("invenio") is not None,
            "data_location_type": request.form["data-location-type"],
            "data_location": request.form["data-location"],
            "db_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "uid": "",
        }

        project1_id = data_info["project1_id"]
        project2_id = data_info["project2_id"]

        if project1_id != project2_id and project2_id != "-1":
            project1_code, project2_code = get_projectdao().get_projects_from_id(
                project1_id, project2_id
            )
        else:
            project1_code = get_projectdao().get_projects_from_id(
                project1_id
            )[0]
            project2_id = ""
            data_info["project2_id"] = "-1"
            project2_code = "XX"

        data_id = get_datadao().fetch_last_data_id() 
        data_id = str(1).zfill(3) if data_id is None else str(data_id + 1).zfill(3)
        id_date = datetime.now().strftime("%Y%m%d")
        uid = f"CRC{id_date}{data_id}{project1_code[0]}{project2_code[0]}"
        data_info["uid"] = uid

        get_datadao().create_data(data_info=data_info)

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
    """Downloads the README file."""
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
    """Update a data entry in the database."""
    user_id = session["user_id"]
    data_entries = get_datadao().fetch_project_data(user_id)
    return render_template("data/update.html", data_entries=data_entries)


@bp.get("/<int:data_id>")
def fetch_data(data_id):
    """Fetche a data entry from the database."""
    data = get_datadao().fetch_data_by_id(data_id)
    return data


@bp.put("/<int:data_id>")
@login_required
def update_data(data_id):
    """Update a data entry in the database."""
    data_info = {
        "data_name": request.form["data-name"],
        "data_description": request.form["data-description"],
        "data_location_type": request.form["data-location-type"],
        "data_location": request.form["data-location"],
        "invenio": bool(request.form.get("invenio")),
    }
    get_datadao().update_data(data_info=data_info, data_id=data_id)
    data = get_datadao().fetch_data_by_id(data_id)
    return render_template("data/row.html", data=data)


@bp.delete("/<int:data_id>")
@login_required
def remove_data(data_id):
    """Delete a data entry from the database."""
    get_datadao().remove_data(data_id)
    return "<tr>Delete Successful</tr>"


@bp.route("/<int:data_id>/row")
@login_required
def render_datarow(data_id):
    """Render a data row."""
    data = get_datadao().fetch_data_by_id(data_id)
    return render_template("data/row.html", data=data)


@bp.get("/<int:data_id>/edit")
@login_required
def edit_data(data_id):
    """Renders a data row."""
    data = get_datadao().fetch_data_by_id(data_id)
    return render_template("data/edit2.html", data=data)


@bp.post("/location-type")
@login_required
def data_location_field():
    """Fetche data by location type."""
    location = request.form["data-location-type"]
    return render_template("data/location.html", location=location)


@bp.post("/filter")
def filter_data_table():
    """Filters the data table."""
    filters = {
        "data_name_match": request.form["data-name"],
        "from_date": request.form["from-date"],
        "to_date": request.form["to-date"],
        "email": request.form["email"],
        "data_location_type": request.form["data-location-type"],
        "invenio": request.form["invenio"],
        "project": request.form["project"],
        "uid": request.form["uid"],
    }

    session["data"] = get_datadao().fetch_data_table(filters)

    return render_template("data/table-body.html", data_entries=session["data"])


@bp.get("/download-table-csv")
def download_table_csv():
    """Download the data table as a CSV."""
    data = session.get("data", {})
    output = get_datadao().write_to_csv(data)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=output.csv"},
    )


@bp.get("/delete-confirmation/<int:data_id>")
def delete_confirmation(data_id):
    """Display delete confirmation before deletion."""
    return render_template("data/delete-confirmation.html", data_id=data_id)
