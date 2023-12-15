"""
This module defines a Flask blueprint for managing record-related functionality.

The blueprint, named 'record', provides routes for displaying record in a table,
creating new record entries, updating existing record entries, and deleting record entries.

Blueprint Details:
- Blueprint Name: record
- URL Prefix: /record
- Decorators: login_required (applied to all routes)

Routes:
- GET /record/ : Display record entries in a table
- POST /record/record_name: Check if record with a given name already exists
- GET/POST /record/create : Create a new record entry
- GET /record/download/<int:record_id> : Download the README file for a record entry
- GET/POST /record/update : Update a record entry
- DELETE /record/<int:record_id> : Remove a record entry
- GET /record/<int:record_id> : Fetch a record entry
- GET /record/row/<int:record_id> : Render a single record row
- GET /record/edit/<int:record_id> : Render input fields to edit a record entry
- POST /record/location-type : Fetch record by location type
- POST /record/filter : Filter the record table
- GET /record/download-table-csv : Download the record table as a CSV
- GET /record/delete-confirmation/<int:record_id> : Display delete confirmation for a record entry

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

from app.auth import login_required
from app.dao.RecordDao import write_to_csv
from app.db import get_recorddao, get_projectdao, get_userdao

bp = Blueprint("record", __name__, url_prefix="/record")


@bp.route("/")
def display_page():
    """Display record entries in a table."""
    record_entries = get_recorddao().fetch_record_table(filters={})
    session["record"] = record_entries
    projects = get_projectdao().fetch_projects()
    emails = get_userdao().fetch_user_emails()
    print(emails)
    emails = [email[0] for email in emails]

    return render_template(
        "record/index.html", record_entries=record_entries, projects=projects, emails=emails
    )


@bp.post("/record_name")
def check_record_name():
    """Check if record with a given name already exists."""
    record_name = request.form["record-name"]
    exists = get_recorddao().fetch_record_by_name(record_name)

    return render_template("record/validation.html", exists=exists)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_record():
    """Create a new record entry in the database."""
    user_id = session["user_id"]
    project_list = get_projectdao().fetch_project_by_user(user_id)

    if request.method == "POST":
        record_info = {
            "user_id": user_id,
            "record_name": request.form["record-name"],
            "project1_id": request.form["project1-id"],
            "project2_id": request.form["project2-id"],
            "record_description": request.form["record-description"],
            "invenio": request.form.get("invenio") is not None,
            "data_location_type": request.form["data-location-type"],
            "data_location": request.form["data-location"],
            "db_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "uid": "",
        }

        project1_id = record_info["project1_id"]
        project2_id = record_info["project2_id"]

        if project1_id != project2_id and project2_id != "0":
            project1_code, project2_code = get_projectdao().get_projects_from_id(
                project1_id, project2_id
            )
        else:
            project1_code = get_projectdao().get_projects_from_id(
                project1_id
            )[0]
            record_info["project2_id"] = "0"
            project2_code = ["XX"]

        record_id = get_recorddao().fetch_last_record_id()
        record_id = str(1).zfill(3) if record_id is None else str(record_id[0] + 1).zfill(3)
        id_date = datetime.now().strftime("%Y%m%d")
        uid = f"CRC{id_date}{record_id}{project1_code[0]}{project2_code[0]}"
        print(uid)
        record_info["uid"] = uid

        get_recorddao().create_record(record_info=record_info)

        download_url = url_for("record.download_readme", record_id=record_id)
        record_page_url = url_for("record.display_page")
        return render_template(
            "record/download.html",
            download_url=download_url,
            record_page_url=record_page_url,
        )
    return render_template("record/create.html", projects=project_list)


@bp.get("/download/<int:record_id>")
@login_required
def download_readme(record_id):
    """Downloads the README file."""
    record = get_recorddao().fetch_record_by_id(record_id)
    record_info = ""
    for key, value in record.items():
        record_info += f"{key}: {value}\n"
    buffer = io.BytesIO()
    buffer.write(record_info.encode("utf-8"))
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
    """Update a record entry in the database."""
    user_id = session["user_id"]
    record_entries = get_recorddao().fetch_project_record(user_id)
    return render_template("record/update.html", record_entries=record_entries)


@bp.get("/<int:record_id>")
def fetch_record(record_id):
    """Fetch a record entry from the database."""
    record = get_recorddao().fetch_record_by_id(record_id)
    return record


@bp.put("/<int:record_id>")
@login_required
def update_record(record_id):
    """Update a record entry in the database."""
    record_info = {
        "record_name": request.form["record-name"],
        "record_description": request.form["record-description"],
        "data_location_type": request.form["data-location-type"],
        "data_location": request.form["data-location"],
        "invenio": bool(request.form.get("invenio")),
    }
    get_recorddao().update_record(record_info=record_info, record_id=record_id)
    record = get_recorddao().fetch_record_by_id(record_id)
    return render_template("record/row.html", record=record)


@bp.delete("/<int:record_id>")
@login_required
def remove_record(record_id):
    """Delete a record entry from the database."""
    get_recorddao().remove_record(record_id)
    return "<tr>Delete Successful</tr>"


@bp.route("/row/<int:record_id>")
@login_required
def render_row(record_id):
    """Render a record row."""
    record = get_recorddao().fetch_record_by_id(record_id)
    return render_template("record/row.html", record=record)


@bp.get("/edit/<int:record_id>")
@login_required
def edit_record(record_id):
    """Renders a record row."""
    record = get_recorddao().fetch_record_by_id(record_id)
    return render_template("record/edit2.html", record=record)


@bp.post("/location-type")
@login_required
def record_location_field():
    """Fetch record by location type."""
    location = request.form["data-location-type"]
    return render_template("record/location.html", location=location)


@bp.post("/filter")
def filter_record_table():
    """Filters the record table."""
    filters = {
        "record_name_match": request.form["record-name"],
        "from_date": request.form["from-date"],
        "to_date": request.form["to-date"],
        "email": request.form["email"],
        "record_location_type": request.form["data-location-type"],
        "invenio": request.form["invenio"],
        "project": request.form["project"],
        "uid": request.form["uid"],
    }

    session["record"] = get_recorddao().fetch_record_table(filters)

    return render_template("record/table-body.html", record_entries=session["record"])


@bp.get("/download-table-csv")
def download_table_csv():
    """Download the record table as a CSV."""
    record = session.get("record", {})
    output = write_to_csv(record)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=output.csv"},
    )


@bp.get("/delete-confirmation/<int:record_id>")
def delete_confirmation(record_id):
    """Display delete confirmation before deletion."""
    return render_template("record/delete-confirmation.html", record_id=record_id)
