from flask import Blueprint, redirect, render_template, request, session, url_for

from models.repositories import get_inventory, mark_notifications_read


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    inventory = get_inventory()
    return render_template("index.html", inventory=inventory)


@main_bp.route("/notifications/read", methods=["POST"])
def read_notifications():
    if session.get("user_id"):
        mark_notifications_read(session["user_id"])
    return redirect(request.referrer or url_for("main.index"))
