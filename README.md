# Library Management System — Milestone 2  
**CS 4347 — Database Systems**

This project is a **Database Host Application** for librarians, backed by a MySQL relational database.  
Milestone 2 extends Milestone 1 by building a working backend service layer, CLI interface, and ETL pipeline, all integrated with a normalized MySQL database.

Librarians can:
- Search for books (by title, author, or ISBN)
- Check out books
- Check in books (with automatic fine computation)
- View borrower info
- View borrower loans (active + historical)
- View and pay fines

---

# Project Features

### Fully normalized MySQL schema (3NF)  
Created in **Milestone 1**, implemented in `schema/schema.sql`.

### ETL pipeline  
`etl/normalize_data.py` → normalizes raw CSVs  
`etl/load_data.py` → loads normalized CSVs into MySQL

### Backend service layer  
Implements core library operations in:

backend/library_service.py

### Manual CLI  
Interactive librarian interface:

python -m backend.manual_cli

### ✔ Smoke tests  
Lightweight test harness verifying the backend:

python -m tests.test_library_service_smoke

---

# 📂 Project Structure

library-management-system/
│
├── backend/
│ ├── init.py
│ ├── db.py # MySQL connections (uses config + .env)
│ ├── models.py # Dataclasses mirroring DB tables
│ ├── utils.py # Row → model converters + helpers
│ ├── library_service.py # Core operations (search, checkout, fines, etc.)
│ └── manual_cli.py # Interactive CLI for librarians
│
├── etl/
│ ├── normalize_data.py # Normalizes raw CSVs into 3NF-compatible files
│ ├── load_data.py # Loads normalized files into MySQL DB
│ └── output/ # Generated normalized CSVs
│
├── schema/
│ ├── schema.sql # MySQL DDL (tables, constraints)
│ ├── sample_data.sql # Insert statements for sample data
│ └── reset.sql # Drops + recreates + reloads schema + data
│
├── tests/
│ └── test_library_service_smoke.py
│
├── raw/ # Raw CSV files (books.csv, borrowers.csv)
│
├── .env.example # Template for DB credentials
├── requirements.txt # Python dependencies
└── README.md


---

# Environment Setup

## 1. Clone the repo

```bash
git clone https://github.com/AJB233/library-management-system.git
cd library-management-system

2. Create + activate virtual environment
bash
python3 -m venv venv
source venv/bin/activate

3. Install dependencies
bash
pip install -r requirements.txt

4. Create .env file
Copy the example:

bash
cp .env.example .env

Edit your DB credentials:

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=library

Database Setup (MySQL)
1. Start MySQL and enter the shell
bash
sudo mysql

2. Run the reset script (recommended)
From the MySQL shell:
sql
SOURCE schema/reset.sql;

This will:

Drop the existing library DB (if any)

Recreate it

Load schema

Load sample data

(Optional) Rebuild DB using ETL pipeline
Normalize the raw CSVs:
bash
python etl/normalize_data.py \
  --books "raw/books(1).csv" \
  --borrowers "raw/borrowers(1).csv" \
  --outdir etl/output

Load normalized data:
bash
python etl/load_data.py

This uses credentials in .env.

💻 Running the Manual CLI
From project root:

bash
source venv/bin/activate
python -m backend.manual_cli

You will see an interactive menu with options for:

Search books

Check out books

Check in books

Borrower lookup

View loans

View/pay fines

Perfect for demos & grading.

Running Smoke Tests
From project root:

bash
source venv/bin/activate
python -m tests.test_library_service_smoke

This verifies:

DB connectivity

Search functionality

Borrower lookup

Loan/fine logic (manual tests optional)

You may set these inside the file to run live checkout/checkin tests:

python
Copy code
KNOWN_TEST_ISBN = "..."
KNOWN_TEST_CARD_ID = "..."
KNOWN_TEST_LOAN_ID = ...