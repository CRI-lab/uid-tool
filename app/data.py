from flask import Blueprint, render_template
from app.db import get_db

bp = Blueprint("data", __name__, url_prefix="/data")


@bp.route("/", methods=["GET", "POST"])
def datapage():
    return render_template("data/index.html")
