from flask import Flask

from config import Config
from routes.admin import admin_bp
from routes.api import api_bp
from routes.auth import auth_bp
from routes.donor import donor_bp
from routes.hospital import hospital_bp
from routes.inventory import inventory_bp
from routes.main import main_bp
from utils.db import init_db_pool


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db_pool(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(hospital_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_globals():
        return {"app_name": "BloodBridge"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

