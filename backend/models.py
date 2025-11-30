# models.py

from typing import List, Optional

class Book:
    """Mirrors the essential attributes of the BOOK table."""
    def __init__(self, isbn: str, title: str):
        self.isbn = isbn
        self.title = title

class Author:
    """Mirrors the AUTHORS table."""
    def __init__(self, author_id: int, name: str):
        self.author_id = author_id
        self.name = name

# Don't need Author and Book_Authors I think

class Borrower:
    """Mirrors the BORROWER table."""
    def __init__(self, card_id: str, ssn: str, bname: str, address: str, phone: Optional[str]):
        # Attributes are in the order Card_id, Ssn, Bname, Address, Phone
        self.card_id = card_id
        self.ssn = ssn
        self.bname = bname
        self.address = address
        # Phone can be NULL 
        self.phone = phone

class BookLoan:
    """Mirrors the BOOK_LOANS table."""
    def __init__(self, loan_id: int, isbn: str, card_id: str, date_out: str, due_date: str, date_in: Optional[str] = None):
        self.loan_id = loan_id
        self.isbn = isbn
        self.card_id = card_id
        self.date_out = date_out
        self.due_date = due_date
        # date_in is Optional[str] because it is NULL for active loans
        self.date_in = date_in

class Fine:
    """Mirrors the FINES table."""
    def __init__(self, loan_id: int, fine_amt: float, paid: bool):
        self.loan_id = loan_id
        # fine_amt (REAL/DECIMAL) is mapped to float
        self.fine_amt = fine_amt
        # paid (INTEGER 0/1) is mapped to boolean for clarity
        self.paid = paid
