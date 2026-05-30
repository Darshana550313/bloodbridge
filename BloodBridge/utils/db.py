from contextlib import contextmanager

import pymysql
from dbutils.pooled_db import PooledDB
from flask import current_app


pool = None


def init_db_pool(app):
    """Initialize a reusable MySQL connection pool for AWS RDS or local MySQL."""
    global pool
    pool = PooledDB(
        creator=pymysql,
        maxconnections=12,
        mincached=2,
        maxcached=6,
        blocking=True,
        ping=1,
        host=app.config["MYSQL_HOST"],
        port=app.config["MYSQL_PORT"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
        charset=app.config["MYSQL_CHARSET"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def ensure_interaction_schema():
    """Create interactive workflow tables when an existing local DB is reused."""
    statements = [
        """
        CREATE TABLE IF NOT EXISTS donation_responses (
            response_id INT AUTO_INCREMENT PRIMARY KEY,
            request_id INT NOT NULL,
            donor_id INT NOT NULL,
            message VARCHAR(255) NULL,
            preferred_date DATE NULL,
            units INT NOT NULL DEFAULT 1 CHECK (units > 0),
            response_status ENUM('Pending', 'Accepted', 'Contacted', 'Scheduled', 'Completed', 'Rejected') NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uq_response_request_donor (request_id, donor_id),
            CONSTRAINT fk_responses_request FOREIGN KEY (request_id) REFERENCES blood_requests(request_id) ON DELETE CASCADE,
            CONSTRAINT fk_responses_donor FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(140) NOT NULL,
            message VARCHAR(255) NOT NULL,
            link VARCHAR(255) NULL,
            is_read BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        "CREATE INDEX idx_responses_status ON donation_responses (response_status, created_at)",
        "CREATE INDEX idx_notifications_user_read ON notifications (user_id, is_read, created_at)",
    ]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for statement in statements:
                try:
                    cursor.execute(statement)
                except pymysql.err.OperationalError as exc:
                    if exc.args[0] != 1061:
                        raise


@contextmanager
def get_connection():
    """Provide a pooled connection and always return it to the pool."""
    if pool is None:
        raise RuntimeError("Database pool is not initialized")

    connection = pool.connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        current_app.logger.exception("Database operation failed")
        raise
    finally:
        connection.close()


def fetch_one(sql, params=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()


def fetch_all(sql, params=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()


def execute(sql, params=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.lastrowid
