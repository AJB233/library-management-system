# backend/db.py
"""
Database connection helpers for the Library Management System.

This module connects to the MySQL database defined in schema/schema.sql.
Connection parameters are loaded from environment variables via config.py.
"""

from contextlib import contextmanager
from typing import Iterator

import mysql.connector
from mysql.connector import MySQLConnection
import config


def get_connection() -> MySQLConnection:
    """
    Return a connection to the MySQL 'library' database.

    Uses the values defined in .env and loaded by config.py:
      - DB_HOST
      - DB_PORT
      - DB_USER
      - DB_PASSWORD
      - DB_NAME
    """
    return mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
    )


@contextmanager
def get_cursor(commit: bool = False, dictionary: bool = True) -> Iterator:
    """
    Context manager that yields a cursor and ensures the connection is closed.

    Example:
        from backend.db import get_cursor

        with get_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM BOOK")
            (count,) = cur.fetchone()

    Args:
        commit: if True, commit the transaction when the block exits.
        dictionary: if True, returns rows as dicts (column_name -> value).

    Yields:
        A MySQL cursor object.
    """
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=dictionary)
        yield cur
        if commit:
            conn.commit()
    finally:
        cur.close()
        conn.close()


def setup_database() -> None:
    """
    Placeholder for compatibility with earlier SQLite-based design.

    In this project, the schema is managed via:
      - schema/schema.sql
      - schema/reset.sql

    So this function does not create tables. It simply checks that we can
    connect to the database; callers can log or handle errors as needed.
    """
    # Simple connectivity check
    conn = get_connection()
    conn.close()
