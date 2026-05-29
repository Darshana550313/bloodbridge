from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models.repositories import create_user, find_user_by_email, upsert_hospital_for_user
from utils.validators import valid_email, valid_phone


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "donor")

        if not name or not valid_email(email) or len(password) < 8:
            flash("Enter a valid name, email, and password with at least 8 characters.", "danger")
            return render_template("register.html")

        if role not in ("donor", "hospital", "blood_bank", "admin"):
            flash("Invalid role selected.", "danger")
            return render_template("register.html")

        if find_user_by_email(email):
            flash("An account with this email already exists.", "warning")
            return render_template("register.html")

        user_id = create_user(name, email, generate_password_hash(password), role)

        if role == "hospital":
            hospital_name = request.form.get("hospital_name", name).strip()
            city = request.form.get("city", "").strip()
            contact = request.form.get("contact", "").strip()
            if not city or not valid_phone(contact):
                flash("Hospital accounts need a valid city and contact number.", "danger")
                return render_template("register.html")
            upsert_hospital_for_user(user_id, hospital_name, city, contact)

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = find_user_by_email(email)

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["name"] = user["name"]
        session["role"] = user["role"]
        flash(f"Welcome back, {user['name']}!", "success")

        dashboards = {
            "donor": "donor.dashboard",
            "hospital": "hospital.dashboard",
            "blood_bank": "inventory.dashboard",
            "admin": "admin.dashboard",
        }
        return redirect(url_for(dashboards.get(user["role"], "main.index")))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))

