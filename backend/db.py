# db.py

import sqlite3

DB_FILE = 'library.db'

def get_connection():
    """Returns a connection object to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    # Allows column access by name instead of index
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """
    Initializes the database schema if it doesn't exist.
    This should be run once when the application first starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Schema definition
    schema_sql = """
    -- BOOK Table
    CREATE TABLE IF NOT EXISTS BOOK (
        isbn TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        -- Add any other non-required columns if needed
        UNIQUE(isbn)
    );

    -- AUTHORS Table
    CREATE TABLE IF NOT EXISTS AUTHORS (
        author_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );

    -- BOOK_AUTHORS Table (Many-to-Many)
    CREATE TABLE IF NOT EXISTS BOOK_AUTHORS (
        author_id INTEGER,
        isbn TEXT,
        PRIMARY KEY (author_id, isbn),
        FOREIGN KEY (author_id) REFERENCES AUTHORS(author_id),
        FOREIGN KEY (isbn) REFERENCES BOOK(isbn)
    );
    
    -- BORROWER Table (Use card_id for card_no requirement)
    CREATE TABLE IF NOT EXISTS BORROWER (
        card_id TEXT PRIMARY KEY,
        bname TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT,
        ssn TEXT NOT NULL UNIQUE
    );
    
    -- BOOK_LOANS Table (Note: date_in is NULL for active loans)
    CREATE TABLE IF NOT EXISTS BOOK_LOANS (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT NOT NULL,
        card_id TEXT NOT NULL,
        date_out TEXT NOT NULL,
        due_date TEXT NOT NULL,
        date_in TEXT, -- NULL if not returned
        FOREIGN KEY (isbn) REFERENCES BOOK(isbn),
        FOREIGN KEY (card_id) REFERENCES BORROWER(card_id)
    );
    
    -- FINES Table
    CREATE TABLE IF NOT EXISTS FINES (
        loan_id INTEGER PRIMARY KEY,
        fine_amt REAL NOT NULL, -- Use REAL for decimal in SQLite
        paid INTEGER NOT NULL DEFAULT 0, -- 0 for FALSE, 1 for TRUE
        FOREIGN KEY (loan_id) REFERENCES BOOK_LOANS(loan_id)
    );
    """
    
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()

# Call this once to ensure the database file and tables exist
# setup_database()
