# Library Management System – Milestone 2
Backend host application and SQL schema for our CS 4347 Database Systems group project.
Backend Host Application + ETL Pipeline + MySQL Database

This project implements a Library Management System for use by librarians.
Milestone 2 introduces:

A Python ETL pipeline (normalize → load)
A MySQL relational schema
A database host application (in progress)
Support for a clean .env-based configuration
A reset workflow for testing & development

Project Structure
library-management-system/
├── backend/                 # Future host application (Milestone 2+)
├── etl/
│   ├── normalize_data.py    # Normalizes raw CSVs → 3NF-compatible output
│   ├── load_data.py         # Loads normalized CSVs into MySQL
│   ├── output/              # Generated normalized CSVs (ignored from Git)
│   └── raw/                 # Provided raw datasets (books + borrowers)
├── schema/
│   ├── schema.sql           # Creates database + tables
│   ├── sample_data.sql      # Optional starter data for DB testing
│   └── reset.sql            # Drops + recreates DB + auto-loads schema/data
├── tests/
│   └── check_counts.py      # (Optional) sanity-check utilities
├── config.py                # Loads DB credentials from .env
├── .env.example             # Template for local .env configurations
├── requirements.txt         # Python dependencies for ETL/backend
└── README.md

Getting Started (Development Setup)
1. Clone the Repository
git clone https://github.com/ajb233/library-management-system.git
cd library-management-system

2. Create and Activate a Python Virtual Environment (WSL)
python3 -m venv venv
source venv/bin/activate

Your prompt should look like:
(venv) user@machine:~/library-management-system$

3. Install Dependencies
pip install -r requirements.txt

4. Create Your Local .env File
Copy the example:
cp .env.example .env

Open it:
nano .env

Fill in your DB credentials:
DB_HOST=localhost
DB_PORT=3306
DB_USER=library_user
DB_PASSWORD=libpass123
DB_NAME=library

DON'T commit your .env file — it is already in .gitignore.

MySQL Setup and Database Reset
1. Start MySQL (if not already running)

sudo service mysql start

2. Load or Reset the Database

The reset script:
Drops the database (if it exists)
Recreates it
Loads schema.sql
Loads sample_data.sql

Run inside MySQL:

sudo mysql

Then:

SOURCE /home/<your-username>/library-management-system/schema/reset.sql;
EXIT;

(Replace <your-username> as needed.)

ETL Pipeline (Normalize → Load)
1. Normalize Raw CSVs
Produces cleaned, 3NF-compatible CSVs under etl/output/.

Run:

python etl/normalize_data.py \
    --books "etl/raw/books(1).csv" \
    --borrowers "etl/raw/borrowers(1).csv" \
    --outdir etl/output


Successful output example:
Wrote 25001 books, 15602 authors, 30340 links, 1000 borrowers

2. Load Normalized Data into MySQL
python etl/load_data.py

If .env is correct and DB user has privileges, you’ll see successful insert logs.

3. Verify Data in MySQL
sudo mysql
USE library;

SELECT COUNT(*) FROM BOOK;
SELECT COUNT(*) FROM AUTHORS;
SELECT COUNT(*) FROM BOOK_AUTHORS;
SELECT COUNT(*) FROM BORROWER;

Testing Utilities
Row count sanity check:
python tests/check_counts.py

Milestone 2: Backend Development (Host Application)

Backend will eventually support:

Searching books

Viewing borrowers

Checking out items

Returning items

Viewing loan history

Managing book/author records

Architecture will follow a clean separation:

backend/
├── db/
│   └── connection.py
├── services/
│   ├── books.py
│   ├── borrowers.py
│   ├── loans.py
│   └── authors.py
├── cli/
└── utils/

Team Workflow
For each team member:

Pull latest changes:

git pull


Create .env from .env.example

Create & activate venv

Run:

pip install -r requirements.txt


Reset and load DB

Run ETL if needed:

python etl/normalize_data.py ...
python etl/load_data.py

This README documents:



Environment setup
## Tech Stack
- **Database:** MySQL  
- **Backend Language:** Python  
- **ETL:** Python + pandas  

## Project Structure
- `schema/` — MySQL schema + sample inserts  
- `etl/` — normalization + loading into DB  
- `backend/` — Python logic (search, checkout, borrowers, fines)  
- `tests/` — manual CLI + automated tests  
- `docs/` — milestone writeups and planning  

## How to Run
See `schema/schema.sql` for database creation.
Use `etl/load_data.py` to populate normalized data.
Use `tests/manual_cli.py` to run backend functions interactively.

