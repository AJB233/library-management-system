-- Full reset + automatic schema & sample data repopulation

DROP DATABASE IF EXISTS library;
CREATE DATABASE library;
USE library;

-- Make sure to run this file using:
--   mysql -u root -p (<--from inside the mysql shell)
-- so that SOURCE commands execute correctly. (wont work from command line)

SOURCE schema/schema.sql;
SOURCE schema/sample_data.sql;
