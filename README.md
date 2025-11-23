# Library Management System – Milestone 2
Backend host application and SQL schema for our CS 4347 Database Systems group project.

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

