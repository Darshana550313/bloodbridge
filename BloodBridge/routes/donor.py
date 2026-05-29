from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.repositories import create_donation, get_donor_by_user, get_matching_requests, upsert_donor
from utils.auth import login_required, role_required
from utils.validators import BLOOD_GROUPS, donor_eligibility, parse_date, valid_phone


donor_bp = Blueprint("donor", __name__, url_prefix="/donor")


@donor_bp.route("/dashboard")
@login_required
@role_required("donor")
def dashboard():
    donor = get_donor_by_user(session["user_id"])
    requests = []
    if donor:
        requests = get_matching_requests(donor["blood_group"], donor["city"])
    return render_template("donor_dashboard.html", donor=donor, requests=requests, blood_groups=BLOOD_GROUPS)


@donor_bp.route("/profile", methods=["POST"])
@login_required
@role_required("donor")
def save_profile():
    blood_group = request.form.get("blood_group")
    city = request.form.get("city", "").strip()
    phone = request.form.get("phone", "").strip()
    last_donation_date = parse_date(request.form.get("last_donation_date"))

    if blood_group not in BLOOD_GROUPS or not city or not valid_phone(phone):
        flash("Please enter a valid blood group, city, and phone number.", "danger")
        return redirect(url_for("donor.dashboard"))

    eligibility = donor_eligibility(last_donation_date)
    upsert_donor(session["user_id"], blood_group, city, phone, last_donation_date, eligibility)
    flash(f"Profile saved. Current eligibility: {eligibility}.", "success")
    return redirect(url_for("donor.dashboard"))


@donor_bp.route("/donate", methods=["POST"])
@login_required
@role_required("donor")
def schedule_donation():
    donor = get_donor_by_user(session["user_id"])
    if not donor:
        flash("Complete your donor profile before scheduling a donation.", "warning")
        return redirect(url_for("donor.dashboard"))

    donation_date = parse_date(request.form.get("donation_date")) or date.today()
    try:
        units = int(request.form.get("units", "1"))
    except ValueError:
        units = 0
    if units < 1 or units > 4:
        flash("Donation units must be between 1 and 4.", "danger")
        return redirect(url_for("donor.dashboard"))

    create_donation(donor["donor_id"], donation_date, donor["blood_group"], units)
    upsert_donor(
        session["user_id"],
        donor["blood_group"],
        donor["city"],
        donor["phone"],
        donation_date,
        donor_eligibility(donation_date),
    )
    flash("Donation scheduled and recorded successfully.", "success")
    return redirect(url_for("donor.dashboard"))
