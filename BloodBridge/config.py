import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-before-production")

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "bloodbridge")
    MYSQL_CHARSET = "utf8mb4"

    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "alerts@bloodbridge.local")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"

    LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "10"))
