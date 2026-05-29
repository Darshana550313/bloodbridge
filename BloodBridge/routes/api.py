from flask import Blueprint, jsonify

from models.repositories import get_all_requests, get_inventory
from utils.auth import login_required


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/inventory")
@login_required
def inventory_data():
    rows = get_inventory()
    return jsonify(
        {
            "labels": [row["blood_group"] for row in rows],
            "units": [row["units_available"] for row in rows],
        }
    )


@api_bp.route("/requests")
@login_required
def request_data():
    rows = get_all_requests()
    return jsonify(
        [
            {
                "request_id": row["request_id"],
                "hospital_name": row["hospital_name"],
                "blood_group": row["blood_group"],
                "quantity": row["quantity"],
                "urgency": row["urgency"],
                "city": row["city"],
                "status": row["request_status"],
            }
            for row in rows
        ]
    )

