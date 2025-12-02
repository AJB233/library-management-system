# tests/test_library_service_smoke.py
"""
Lightweight smoke tests for backend.library_service.

Run with:
    python tests/test_library_service_smoke.py

These tests are not strict unit tests; they are sanity checks to confirm
that the service functions can be called without crashing and that they
interact with the database in a plausible way.

NOTE:
    For some tests (checkout/checkin/fines), you will need to plug in
    real values (ISBN, Card_id, Loan_id) that exist in your database.
"""

from __future__ import annotations

from typing import Optional

from backend import library_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_banner(name: str) -> None:
    print("\n" + "=" * 60)
    print(f"[TEST] {name}")
    print("=" * 60)


def _safe_run(name: str, func) -> None:
    _print_banner(name)
    try:
        func()
        print(f"[OK] {name}")
    except Exception as e:
        print(f"[FAILED] {name}: {e}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_search_books_basic() -> None:
    term = "harry"  # or some other likely-but-not-crazy term
    results = library_service.search_books(term)
    print(f"search_books({term!r}) returned {len(results)} result(s).")
    if results:
        print("Sample:", results[0])


def test_get_borrower_not_found() -> None:
    card_id = "NON_EXISTENT_CARD_ID_12345"
    borrower = library_service.get_borrower(card_id)
    assert borrower is None
    print(f"get_borrower({card_id!r}) correctly returned None.")


def test_get_borrower_loans_empty() -> None:
    card_id = "NON_EXISTENT_CARD_ID_12345"
    loans = library_service.get_borrower_loans(card_id)
    assert loans == []
    print(f"get_borrower_loans({card_id!r}) returned empty list as expected.")


def test_get_borrower_fines_empty() -> None:
    card_id = "NON_EXISTENT_CARD_ID_12345"
    fines = library_service.get_borrower_fines(card_id)
    assert fines == []
    print(f"get_borrower_fines({card_id!r}) returned empty list as expected.")


# These tests require REAL data in your DB.
# Fill in values that you know exist to exercise the full flow.

KNOWN_TEST_ISBN: Optional[str] = None      # e.g. "0439064872"
KNOWN_TEST_CARD_ID: Optional[str] = None   # e.g. "ID0001"
KNOWN_TEST_LOAN_ID: Optional[int] = None   # e.g. 42


def test_checkout_book_manual() -> None:
    if not KNOWN_TEST_ISBN or not KNOWN_TEST_CARD_ID:
        print("Skipping checkout test; set KNOWN_TEST_ISBN and KNOWN_TEST_CARD_ID to real values.")
        return
    success, msg = library_service.checkout_book(KNOWN_TEST_ISBN, KNOWN_TEST_CARD_ID)
    print("checkout_book:", success, msg)


def test_checkin_book_manual() -> None:
    if KNOWN_TEST_LOAN_ID is None:
        print("Skipping checkin test; set KNOWN_TEST_LOAN_ID to a real value.")
        return
    success, msg = library_service.checkin_book(KNOWN_TEST_LOAN_ID)
    print("checkin_book:", success, msg)


def test_pay_fine_manual() -> None:
    if KNOWN_TEST_LOAN_ID is None:
        print("Skipping pay_fine test; set KNOWN_TEST_LOAN_ID to a real value.")
        return
    success, msg = library_service.pay_fine(KNOWN_TEST_LOAN_ID)
    print("pay_fine:", success, msg)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main() -> None:
    _safe_run("search_books_basic", test_search_books_basic)
    _safe_run("get_borrower_not_found", test_get_borrower_not_found)
    _safe_run("get_borrower_loans_empty", test_get_borrower_loans_empty)
    _safe_run("get_borrower_fines_empty", test_get_borrower_fines_empty)

    _safe_run("checkout_book_manual", test_checkout_book_manual)
    _safe_run("checkin_book_manual", test_checkin_book_manual)
    _safe_run("pay_fine_manual", test_pay_fine_manual)


if __name__ == "__main__":
    main()
