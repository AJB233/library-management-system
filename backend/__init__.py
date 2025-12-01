"""
Backend package for the Library Management System.

This package is responsible for talking to the database layer and
exposing Python model objects that mirror the MySQL schema defined in
schema/schema.sql.

Core modules:
    - db:    connection helpers for MySQL (uses config.py / .env)
    - models: dataclasses that represent BOOK, AUTHORS, BORROWER, etc.
    - utils: helpers for converting DB rows into models and common
             parsing/formatting utilities.
"""

from . import db
from . import models
from . import utils

__all__ = [
    "db",
    "models",
    "utils",
]
