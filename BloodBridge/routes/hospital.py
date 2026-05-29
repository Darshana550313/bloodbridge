from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.repositories import (
    create_blood_request,
    find_matching_donors,
    get_hospital_by_user,
    get_requests_for_hospital,
    update_request_status,
    upsert_hospital_for_user,
)
from utils.auth import login_required, role_required
from utils.notifications import send_email_notification, send_sms_alert
from utils.validators import BLOOD_GROUPS, URGENCY_LEVELS, valid_phone


hospital_bp = Blueprint("hospital", __name__, url_prefix="/hospital")


@hospital_bp.route("/dashboard")
@login_required
@role_required("hospital")
def dashboard():
    hospital = get_hospital_by_user(session["user_id"])
    requests = get_requests_for_hospital(hospital["hospital_id"]) if hospital else []
    matching_donors = []
    if requests:
        newest = requests[0]
        matching_donors = find_matching_donors(newest["blood_group"], newest["city"])
    return render_template(
        "hospital_dashboard.html",
        hospital=hospital,
        requests=requests,
        matching_donors=matching_donors,
        blood_groups=BLOOD_GROUPS,
        urgency_levels=URGENCY_LEVELS,
    )


@hospital_bp.route("/profile", methods=["POST"])
@login_required
@role_required("hospital")
def save_profile():
    hospital_name = request.form.get("hospital_name", "").strip()
    city = request.form.get("city", "").strip()
    contact = request.form.get("contact", "").strip()
    if not hospital_name or not city or not valid_phone(contact):
        flash("Hospital name, city, and contact are required.", "danger")
        return redirect(url_for("hospital.dashboard"))

    upsert_hospital_for_user(session["user_id"], hospital_name, city, contact)
    flash("Hospital profile saved.", "success")
    return redirect(url_for("hospital.dashboard"))


@hospital_bp.route("/request", methods=["GET", "POST"])
@login_required
@role_required("hospital")
def request_blood():
    hospital = get_hospital_by_user(session["user_id"])
    if request.method == "POST":
        if not hospital:
            flash("Complete your hospital profile before creating requests.", "warning")
            return redirect(url_for("hospital.dashboard"))

        blood_group = request.form.get("blood_group")
        urgency = request.form.get("urgency")
        city = request.form.get("city", hospital["city"]).strip()
        try:
            quantity = int(request.form.get("quantity", "1"))
        except ValueError:
            quantity = 0

        if blood_group not in BLOOD_GROUPS or urgency not in URGENCY_LEVELS or quantity < 1:
            flash("Please enter valid request details.", "danger")
            return redirect(url_for("hospital.request_blood"))

        request_id = create_blood_request(hospital["hospital_id"], blood_group, quantity, urgency, city)
        donors = find_matching_donors(blood_group, city)
        for donor in donors[:5]:
            send_email_notification(
                donor["email"],
                "Emergency blood request nearby",
                f"{hospital['hospital_name']} needs {quantity} unit(s) of {blood_group} blood in {city}.",
            )
            send_sms_alert(donor["phone"], f"BloodBridge alert: {blood_group} request in {city}.")

        flash(f"Emergency request #{request_id} created. {len(donors)} matching donor(s) found.", "success")
        return redirect(url_for("hospital.dashboard"))

    return render_template("request_blood.html", hospital=hospital, blood_groups=BLOOD_GROUPS, urgency_levels=URGENCY_LEVELS)


@hospital_bp.route("/request/<int:request_id>/status", methods=["POST"])
@login_required
@role_required("hospital")
def change_request_status(request_id):
    hospital = get_hospital_by_user(session["user_id"])
    status = request.form.get("request_status")
    if status not in ("Open", "In Progress", "Fulfilled", "Cancelled"):
        flash("Invalid request status.", "danger")
        return redirect(url_for("hospital.dashboard"))

    update_request_status(request_id, hospital["hospital_id"], status)
    flash("Request status updated.", "success")
    return redirect(url_for("hospital.dashboard"))
