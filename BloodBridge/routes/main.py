from flask import Blueprint, render_template

from models.repositories import get_inventory


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    inventory = get_inventory()
    return render_template("index.html", inventory=inventory)

