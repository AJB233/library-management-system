# backend/utils.py
"""
Utility helpers for the Library Management System backend.

Includes:
  - Converters from DB rows (dicts) to model instances
  - Date and boolean helpers

These helpers are intentionally lightweight so that library_service.py
and manual_cli.py can stay focused on application logic instead of
repeating row→model conversion everywhere.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from typing import Any, Mapping, Optional

from .models import Book, Author, BookAuthor, Borrower, BookLoan, Fine


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def to_bool(value: Any) -> bool:
    """
    Convert typical MySQL boolean-ish values to a Python bool.

    Accepts 0/1, '0'/'1', True/False, or anything truthy/falsy.
    """
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip() not in ("0", "", "false", "False", "FALSE")
    return bool(value)


def parse_date(value: Any) -> Optional[date]:
    """
    Normalize a DATE-like value from MySQL into a Python date.

    Handles:
      - None
      - datetime.date
      - datetime.datetime
      - ISO-8601 strings (e.g. '2025-01-20')
    """
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    # Fallback: assume string in ISO format
    return date.fromisoformat(str(value))


def date_to_str(d: Optional[date]) -> Optional[str]:
    """Convert a date to 'YYYY-MM-DD' string or return None."""
    if d is None:
        return None
    return d.isoformat()


# ---------------------------------------------------------------------------
# Row → model converters
# ---------------------------------------------------------------------------

def _get(row: Mapping[str, Any], *keys: str) -> Any:
    """
    Helper to get a field from a row using possible alternative keys.

    Example:
        _get(row, "Isbn", "isbn")

    This is useful because MySQL column names are often `Isbn`, `Title`, etc.,
    but queries might alias them to lower_snake_case.
    """
    for k in keys:
        if k in row:
            return row[k]
    raise KeyError(f"None of keys {keys} found in row: {row!r}")


def row_to_book(row: Mapping[str, Any]) -> Book:
    return Book(
        isbn=_get(row, "Isbn", "isbn"),
        title=_get(row, "Title", "title"),
    )


def row_to_author(row: Mapping[str, Any]) -> Author:
    return Author(
        author_id=int(_get(row, "Author_id", "author_id", "id")),
        name=_get(row, "Name", "name"),
    )


def row_to_book_author(row: Mapping[str, Any]) -> BookAuthor:
    return BookAuthor(
        isbn=_get(row, "Isbn", "isbn"),
        author_id=int(_get(row, "Author_id", "author_id")),
    )


def row_to_borrower(row: Mapping[str, Any]) -> Borrower:
    return Borrower(
        card_id=_get(row, "Card_id", "card_id"),
        ssn=_get(row, "Ssn", "ssn"),
        bname=_get(row, "Bname", "bname", "name"),
        address=_get(row, "Address", "address"),
        phone=_get(row, "Phone", "phone"),
    )


def row_to_book_loan(row: Mapping[str, Any]) -> BookLoan:
    return BookLoan(
        loan_id=int(_get(row, "Loan_id", "loan_id", "id")),
        isbn=_get(row, "Isbn", "isbn"),
        card_id=_get(row, "Card_id", "card_id"),
        date_out=str(_get(row, "Date_out", "date_out")),
        due_date=str(_get(row, "Due_date", "due_date")),
        date_in=_get(row, "Date_in", "date_in"),
    )


def row_to_fine(row: Mapping[str, Any]) -> Fine:
    return Fine(
        loan_id=int(_get(row, "Loan_id", "loan_id")),
        fine_amt=float(_get(row, "Fine_amt", "fine_amt")),
        paid=to_bool(_get(row, "Paid", "paid")),
    )


# ---------------------------------------------------------------------------
# Small helpers that might be handy for CLI / debugging
# ---------------------------------------------------------------------------

def model_to_dict(obj: Any) -> dict:
    """
    Convert a dataclass model to a plain dict.

    This is convenient for JSON, pretty-printing, or templating.
    """
    try:
        return asdict(obj)
    except TypeError:
        # Not a dataclass; fall back to __dict__ if available
        return getattr(obj, "__dict__", dict())
