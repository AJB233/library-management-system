# backend/manual_cli.py
"""
Manual CLI for the Library Management System.

This is a simple text-based interface for librarians to interact
with library_service.py

It assumes:
  - MySQL is running
  - The 'library' database is set up (schema/reset.sql)
  - Data has been loaded via the ETL pipeline
  - .env is correctly configured

Run with:
    python -m backend.manual_cli
or from repo root (if PYTHONPATH is set):
    python backend/manual_cli.py
"""

from __future__ import annotations

import sys
from typing import Any, Dict

from . import library_service


def _print_header(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def _print_result(obj: Any) -> None:
    """Pretty-print dicts or simple values."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"  {k}: {v}")
    else:
        print(obj)


def action_search_books() -> None:
    query = input("Enter title/author/ISBN search term: ").strip()
    if not query:
        print("Search term cannot be empty.")
        return

    _print_header(f"Search results for '{query}'")
    results = library_service.search_books(query)
    if not results:
        print("No matching books found.")
        return

    for i, entry in enumerate(results, start=1):
        book = entry["book"]
        authors = ", ".join(entry["authors"]) or "<Unknown>"
        status = "Available" if entry["available"] else "Checked out"
        print(f"{i}. {book['isbn']} — {book['title']}")
        print(f"   Authors: {authors}")
        print(f"   Status:  {status}")
        print("-" * 60)


def action_checkout_book() -> None:
    isbn = input("Enter ISBN to check out: ").strip()
    card_id = input("Enter borrower Card_id: ").strip()

    success, msg = library_service.checkout_book(isbn, card_id)
    print("\n" + msg)
    if not success:
        print("Checkout failed.")
    else:
        print("Checkout successful.")


def action_checkin_book() -> None:
    loan_id_str = input("Enter Loan_id to check in: ").strip()
    if not loan_id_str.isdigit():
        print("Loan_id must be an integer.")
        return

    loan_id = int(loan_id_str)
    success, msg = library_service.checkin_book(loan_id)
    print("\n" + msg)
    if not success:
        print("Checkin failed.")
    else:
        print("Checkin successful.")


def action_view_borrower_loans() -> None:
    card_id = input("Enter borrower Card_id: ").strip()
    include_history = input("Include history? (y/N): ").strip().lower() == "y"

    loans = library_service.get_borrower_loans(card_id, include_history=include_history)
    _print_header(f"Loans for borrower {card_id}")
    if not loans:
        print("No loans found (or borrower may not exist).")
        return

    for entry in loans:
        loan = entry["loan"]
        print(f"Loan_id:   {loan['loan_id']}")
        print(f"  ISBN:     {loan['isbn']}")
        print(f"  Title:    {entry['book_title']}")
        print(f"  Date out: {loan['date_out']}")
        print(f"  Due date: {loan['due_date']}")
        print(f"  Date in:  {loan['date_in']}")
        print(f"  Active:   {entry['is_active']}")
        print("-" * 60)


def action_view_borrower_fines() -> None:
    card_id = input("Enter borrower Card_id: ").strip()
    only_unpaid = input("Only unpaid fines? (Y/n): ").strip().lower() != "n"

    fines = library_service.get_borrower_fines(card_id, only_unpaid=only_unpaid)
    _print_header(f"Fines for borrower {card_id}")
    if not fines:
        print("No fines found.")
        return

    for entry in fines:
        fine = entry["fine"]
        print(f"Loan_id:  {fine['loan_id']}")
        print(f"  Amount: ${fine['fine_amt']:.2f}")
        print(f"  Paid:   {fine['paid']}")
        print(f"  Title:  {entry['book_title']}")
        print(f"  Out:    {entry['date_out']}")
        print(f"  Due:    {entry['due_date']}")
        print(f"  In:     {entry['date_in']}")
        print("-" * 60)


def action_pay_fine() -> None:
    loan_id_str = input("Enter Loan_id for fine payment: ").strip()
    if not loan_id_str.isdigit():
        print("Loan_id must be an integer.")
        return

    loan_id = int(loan_id_str)
    success, msg = library_service.pay_fine(loan_id)
    print("\n" + msg)
    if not success:
        print("Payment failed.")
    else:
        print("Payment successful.")


def action_view_borrower() -> None:
    card_id = input("Enter borrower Card_id: ").strip()
    borrower = library_service.get_borrower(card_id)

    _print_header(f"Borrower lookup: {card_id}")
    if borrower is None:
        print("No borrower found.")
        return

    for k, v in borrower.items():
        print(f"{k}: {v}")


def main() -> None:
    actions = {
        "1": ("Search books", action_search_books),
        "2": ("Check out a book", action_checkout_book),
        "3": ("Check in a book", action_checkin_book),
        "4": ("View borrower loans", action_view_borrower_loans),
        "5": ("View borrower fines", action_view_borrower_fines),
        "6": ("Pay a fine", action_pay_fine),
        "7": ("View borrower info", action_view_borrower),
        "0": ("Exit", None),
    }

    while True:
        print("\n" + "=" * 60)
        print(" Library Management System - Manual CLI")
        print("=" * 60)
        for key, (label, _) in actions.items():
            print(f"[{key}] {label}")
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            break

        action = actions.get(choice)
        if not action:
            print("Invalid choice. Please try again.")
            continue

        _, func = action
        try:
            func()
        except Exception as e:
            print(f"\n[ERROR] An exception occurred: {e}")


if __name__ == "__main__":
    main()
