import psycopg2

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname="tax_database",
    user="tax_assistant",
    password="1234",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create the person table
cursor.execute('''
CREATE TABLE IF NOT EXISTS person (
    afm TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    family_status TEXT NOT NULL,
    children INTEGER NOT NULL
)
''')

# Create the tax_details table
cursor.execute('''
CREATE TABLE IF NOT EXISTS tax_details (
    uid TEXT PRIMARY KEY,
    afm TEXT NOT NULL,
    salary REAL NOT NULL,
    freelance REAL NOT NULL,
    rental REAL NOT NULL,
    investments REAL NOT NULL,
    business REAL NOT NULL,
    medical REAL NOT NULL,
    donations REAL NOT NULL,
    insurance REAL NOT NULL,
    renovation REAL NOT NULL,
    property_details TEXT NOT NULL,
    property_value REAL NOT NULL,
    vehicles TEXT NOT NULL,
    tax_prepayments REAL NOT NULL,
    insurance_payments REAL NOT NULL,
    submission_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (afm) REFERENCES person(afm)
)
''')

# Create the users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    afm TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

# Commit the changes and close the connection
conn.commit()
cursor.close()
conn.close()
