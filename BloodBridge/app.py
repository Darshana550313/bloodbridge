from flask import Flask, session

from config import Config
from routes.admin import admin_bp
from routes.api import api_bp
from routes.auth import auth_bp
from routes.donor import donor_bp
from routes.hospital import hospital_bp
from routes.inventory import inventory_bp
from routes.main import main_bp
from utils.db import ensure_interaction_schema, init_db_pool
from models.repositories import get_recent_notifications, get_unread_notification_count


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db_pool(app)
    ensure_interaction_schema()

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(hospital_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_globals():
        user_id = session.get("user_id")
        notifications = []
        unread_notifications = 0
        if user_id:
            notifications = get_recent_notifications(user_id)
            unread_notifications = get_unread_notification_count(user_id)
        return {
            "app_name": "BloodBridge",
            "nav_notifications": notifications,
            "unread_notifications": unread_notifications,
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
