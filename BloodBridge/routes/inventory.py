from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from models.repositories import get_inventory, get_recent_donations, update_inventory
from utils.auth import login_required, role_required
from utils.validators import BLOOD_GROUPS


inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.route("/")
@login_required
@role_required("blood_bank", "admin")
def dashboard():
    inventory = get_inventory()
    donations = get_recent_donations()
    low_stock = [row for row in inventory if row["units_available"] <= current_app.config["LOW_STOCK_THRESHOLD"]]
    return render_template(
        "inventory.html",
        inventory=inventory,
        donations=donations,
        low_stock=low_stock,
        blood_groups=BLOOD_GROUPS,
    )


@inventory_bp.route("/update", methods=["POST"])
@login_required
@role_required("blood_bank", "admin")
def update_stock():
    blood_group = request.form.get("blood_group")
    try:
        units_available = int(request.form.get("units_available", "0"))
    except ValueError:
        units_available = -1
    if blood_group not in BLOOD_GROUPS or units_available < 0:
        flash("Enter a valid blood group and stock count.", "danger")
        return redirect(url_for("inventory.dashboard"))

    update_inventory(blood_group, units_available)
    if units_available <= current_app.config["LOW_STOCK_THRESHOLD"]:
        flash(f"Low stock alert: {blood_group} has only {units_available} unit(s).", "warning")
    else:
        flash("Inventory updated successfully.", "success")
    return redirect(url_for("inventory.dashboard"))
