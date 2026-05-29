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

