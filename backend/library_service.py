"""
library_service.py

Service layer for the Library Management System.

This module exposes high-level operations for use by the host
application (e.g., manual CLI, GUI, etc.) and hides the raw SQL
details behind cleaner Python functions.

Assumptions (matching schema/schema.sql and ETL):
    - BOOK(Isbn, Title)
    - AUTHORS(Author_id, Name)
    - BOOK_AUTHORS(Author_id, Isbn)
    - BORROWER(Card_id, Ssn, Bname, Address, Phone)
    - BOOK_LOANS(Loan_id, Isbn, Card_id, Date_out, Due_date, Date_in)
    - FINES(Loan_id, Fine_amt, Paid)

Key operations:
    - search_books()
    - checkout_book()
    - checkin_book()
    - get_borrower_loans()
    - get_borrower_fines()
    - pay_fine()
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from .db import get_cursor
from . import utils
from .models import BookLoan, Fine, Borrower


# ---------------------------------------------------------------------------
# Helper queries
# ---------------------------------------------------------------------------

def _book_is_available(isbn: str) -> bool:
    """
    Return True if the book has no active (unreturned) loans.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS n
            FROM BOOK_LOANS
            WHERE Isbn = %s AND Date_in IS NULL
            """,
            (isbn,),
        )
        row = cur.fetchone()
    return (row or {}).get("n", 0) == 0


def _borrower_active_loan_count(card_id: str) -> int:
    """
    Return the number of active loans for the given borrower.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS n
            FROM BOOK_LOANS
            WHERE Card_id = %s AND Date_in IS NULL
            """,
            (card_id,),
        )
        row = cur.fetchone()
    return int((row or {}).get("n", 0))


def _borrower_exists(card_id: str) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "SELECT 1 FROM BORROWER WHERE Card_id = %s",
            (card_id,),
        )
        row = cur.fetchone()
    return row is not None


# ---------------------------------------------------------------------------
# Public: Searching
# ---------------------------------------------------------------------------

def search_books(query: str) -> List[Dict[str, Any]]:
    """
    Search books by title, author name, or ISBN.

    Returns a list of dictionaries with:
        - book: Book model as dict
        - authors: list of author names
        - available: bool
    """
    like = f"%{query}%"

    with get_cursor() as cur:
        cur.execute(
            """
            SELECT
                b.Isbn,
                b.Title,
                GROUP_CONCAT(a.Name SEPARATOR ', ') AS Authors
            FROM BOOK b
            LEFT JOIN BOOK_AUTHORS ba ON ba.Isbn = b.Isbn
            LEFT JOIN AUTHORS a ON a.Author_id = ba.Author_id
            WHERE b.Title LIKE %s
               OR a.Name LIKE %s
               OR b.Isbn = %s
            GROUP BY b.Isbn, b.Title
            ORDER BY b.Title ASC
            """,
            (like, like, query),
        )
        rows = cur.fetchall()

    results: List[Dict[str, Any]] = []
    for row in rows:
        book = utils.row_to_book(row)
        authors_str = row.get("Authors") or ""
        authors = [name.strip() for name in authors_str.split(",") if name.strip()]
        available = _book_is_available(book.isbn)

        results.append(
            {
                "book": asdict(book),
                "authors": authors,
                "available": available,
            }
        )

    return results


# ---------------------------------------------------------------------------
# Public: Checkout / Checkin
# ---------------------------------------------------------------------------

MAX_ACTIVE_LOANS_PER_BORROWER = 3
LOAN_DAYS = 14
FINE_RATE_PER_DAY = 0.25  # dollars per overdue day


def checkout_book(isbn: str, card_id: str) -> Tuple[bool, str]:
    """
    Attempt to check out a book for the given borrower.

    Rules:
        - Borrower must exist.
        - Borrower may have at most MAX_ACTIVE_LOANS_PER_BORROWER active loans.
        - Book must not already be on loan (Date_in IS NULL).

    On success, creates a BOOK_LOANS row with:
        Date_out = CURDATE()
        Due_date = DATE_ADD(CURDATE(), INTERVAL LOAN_DAYS DAY)
        Date_in = NULL

    Returns (success, message).
    """
    if not _borrower_exists(card_id):
        return False, f"Borrower with Card_id {card_id} does not exist."

    active_loans = _borrower_active_loan_count(card_id)
    if active_loans >= MAX_ACTIVE_LOANS_PER_BORROWER:
        return False, f"Borrower already has {active_loans} active loans."

    if not _book_is_available(isbn):
        return False, f"Book {isbn} is currently checked out."

    # Perform checkout
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in)
            VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s DAY), NULL)
            """,
            (isbn, card_id, LOAN_DAYS),
        )

    return True, f"Book {isbn} successfully checked out to borrower {card_id}."


def checkin_book(loan_id: int) -> Tuple[bool, str]:
    """
    Check in a book by marking Date_in = CURDATE() for the given loan_id.

    Also (re)computes fines:
        - days_late = DATEDIFF(CURDATE(), Due_date)
        - fine_amt = max(0, days_late) * FINE_RATE_PER_DAY
        - Upserts into FINES (loan_id PK):
            INSERT ... ON DUPLICATE KEY UPDATE Fine_amt = new_amt, Paid = 0

    Returns (success, message).
    """
    # Ensure there is an active loan to close
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT Loan_id, Isbn, Card_id, Due_date, Date_in
            FROM BOOK_LOANS
            WHERE Loan_id = %s
            """,
            (loan_id,),
        )
        row = cur.fetchone()

    if row is None:
        return False, f"No loan found with Loan_id={loan_id}."

    loan = utils.row_to_book_loan(row)
    if loan.date_in is not None:
        return False, f"Loan {loan_id} is already closed."

    # Mark as returned and compute/update fines
    with get_cursor(commit=True) as cur:
        # 1) Set Date_in = CURDATE()
        cur.execute(
            """
            UPDATE BOOK_LOANS
            SET Date_in = CURDATE()
            WHERE Loan_id = %s AND Date_in IS NULL
            """,
            (loan_id,),
        )

        # 2) Compute days late and fine
        cur.execute(
            """
            SELECT
                DATEDIFF(CURDATE(), Due_date) AS days_late
            FROM BOOK_LOANS
            WHERE Loan_id = %s
            """,
            (loan_id,),
        )
        late_row = cur.fetchone()
        days_late = int((late_row or {}).get("days_late", 0))

        if days_late > 0:
            fine_amt = days_late * FINE_RATE_PER_DAY
            # Upsert into FINES
            cur.execute(
                """
                INSERT INTO FINES (Loan_id, Fine_amt, Paid)
                VALUES (%s, %s, 0)
                ON DUPLICATE KEY UPDATE
                    Fine_amt = VALUES(Fine_amt),
                    Paid = 0
                """,
                (loan_id, fine_amt),
            )
            msg = (
                f"Book returned. Loan {loan_id} is {days_late} days late. "
                f"Fine applied: ${fine_amt:.2f}."
            )
        else:
            # If not late, ensure no fine exists or is cleared (optional)
            msg = f"Book returned on time for loan {loan_id}. No fine applied."

    return True, msg


# ---------------------------------------------------------------------------
# Public: Borrower views
# ---------------------------------------------------------------------------

def get_borrower_loans(card_id: str, include_history: bool = False) -> List[Dict[str, Any]]:
    """
    Return current (and optionally historical) loans for a borrower.

    Each item includes:
        - loan: BookLoan as dict
        - book_title
        - is_active (bool)
    """
    if not _borrower_exists(card_id):
        return []

    with get_cursor() as cur:
        if include_history:
            cur.execute(
                """
                SELECT bl.*, b.Title
                FROM BOOK_LOANS bl
                JOIN BOOK b ON b.Isbn = bl.Isbn
                WHERE bl.Card_id = %s
                ORDER BY bl.Date_out DESC, bl.Loan_id DESC
                """,
                (card_id,),
            )
        else:
            cur.execute(
                """
                SELECT bl.*, b.Title
                FROM BOOK_LOANS bl
                JOIN BOOK b ON b.Isbn = bl.Isbn
                WHERE bl.Card_id = %s AND bl.Date_in IS NULL
                ORDER BY bl.Date_out DESC, bl.Loan_id DESC
                """,
                (card_id,),
            )
        rows = cur.fetchall()

    results: List[Dict[str, Any]] = []
    for row in rows:
        loan = utils.row_to_book_loan(row)
        is_active = loan.date_in is None
        results.append(
            {
                "loan": asdict(loan),
                "book_title": row.get("Title"),
                "is_active": is_active,
            }
        )
    return results


def get_borrower_fines(card_id: str, only_unpaid: bool = True) -> List[Dict[str, Any]]:
    """
    Return fines associated with a borrower's loans.

    Each item includes:
        - fine: Fine as dict
        - book_title
        - date_out, due_date, date_in
    """
    if not _borrower_exists(card_id):
        return []

    with get_cursor() as cur:
        cur.execute(
            f"""
            SELECT f.*, bl.Isbn, bl.Date_out, bl.Due_date, bl.Date_in, b.Title
            FROM FINES f
            JOIN BOOK_LOANS bl ON bl.Loan_id = f.Loan_id
            JOIN BOOK b ON b.Isbn = bl.Isbn
            WHERE bl.Card_id = %s
              {"AND f.Paid = 0" if only_unpaid else ""}
            ORDER BY bl.Due_date DESC
            """,
            (card_id,),
        )
        rows = cur.fetchall()

    results: List[Dict[str, Any]] = []
    for row in rows:
        fine = Fine(
            loan_id=int(row["Loan_id"]),
            fine_amt=float(row["Fine_amt"]),
            paid=utils.to_bool(row["Paid"]),
        )
        results.append(
            {
                "fine": asdict(fine),
                "book_title": row.get("Title"),
                "date_out": str(row.get("Date_out")),
                "due_date": str(row.get("Due_date")),
                "date_in": str(row.get("Date_in")) if row.get("Date_in") else None,
            }
        )
    return results


def pay_fine(loan_id: int) -> Tuple[bool, str]:
    """
    Mark a fine as paid for the given loan_id.

    Returns (success, message).
    """
    with get_cursor(commit=True) as cur:
        # Check existing fine
        cur.execute(
            "SELECT Loan_id, Fine_amt, Paid FROM FINES WHERE Loan_id = %s",
            (loan_id,),
        )
        row = cur.fetchone()

        if row is None:
            return False, f"No fine found for loan {loan_id}."

        if utils.to_bool(row.get("Paid")):
            return False, f"Fine for loan {loan_id} is already marked as paid."

        cur.execute(
            "UPDATE FINES SET Paid = 1 WHERE Loan_id = %s",
            (loan_id,),
        )

    return True, f"Fine for loan {loan_id} marked as paid."


# ---------------------------------------------------------------------------
# Convenience: simple borrower lookup (for CLI etc.)
# ---------------------------------------------------------------------------

def get_borrower(card_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single borrower by card_id as a dict, or None if not found.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM BORROWER
            WHERE Card_id = %s
            """,
            (card_id,),
        )
        row = cur.fetchone()

    if not row:
        return None

    borrower = Borrower(
        card_id=row["Card_id"],
        ssn=row["Ssn"],
        bname=row["Bname"],
        address=row["Address"],
        phone=row.get("Phone"),
    )
    return asdict(borrower)
