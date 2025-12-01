# backend/models.py
"""
Python model classes that mirror the core tables in the Library database.

These are DB-agnostic and are intended to match the schema defined in
schema/schema.sql (MySQL):

  - BOOK
  - AUTHORS
  - BOOK_AUTHORS
  - BORROWER
  - BOOK_LOANS
  - FINES
"""

from dataclasses import dataclass
from typing import Optional


# -----------------------------
# Core entities
# -----------------------------

@dataclass
class Book:
    """Mirrors the BOOK table."""
    isbn: str
    title: str


@dataclass
class Author:
    """Mirrors the AUTHORS table."""
    author_id: int
    name: str


@dataclass
class BookAuthor:
    """
    Mirrors the BOOK_AUTHORS link table (many-to-many between BOOK and AUTHORS).
    """
    isbn: str
    author_id: int


@dataclass
class Borrower:
    """Mirrors the BORROWER table."""
    card_id: str
    ssn: str
    bname: str
    address: str
    # Phone can be NULL in the DB, so it is Optional here.
    phone: Optional[str]


@dataclass
class BookLoan:
    """Mirrors the BOOK_LOANS table."""
    loan_id: int
    isbn: str
    card_id: str
    # Dates are stored as DATE in MySQL; represented as strings or date objects in code.
    date_out: str
    due_date: str
    # NULL for active loans
    date_in: Optional[str] = None


@dataclass
class Fine:
    """Mirrors the FINES table."""
    loan_id: int
    # DECIMAL(6,2) in MySQL; represented as float here for simplicity.
    fine_amt: float
    # TINYINT(1) in MySQL; mapped to bool in code.
    paid: bool
