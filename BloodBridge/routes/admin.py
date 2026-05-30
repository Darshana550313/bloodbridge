from flask import Blueprint, render_template

from models.repositories import admin_metrics, get_all_donation_responses, get_all_requests, get_all_users, get_inventory
from utils.auth import login_required, role_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    return render_template(
        "admin_dashboard.html",
        metrics=admin_metrics(),
        users=get_all_users(),
        requests=get_all_requests(),
        responses=get_all_donation_responses(),
        inventory=get_inventory(),
    )
