import sqlite3

conn = sqlite3.connect('tax_database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS person (
    afm INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    family_status TEXT NOT NULL,
    children INTEGER NOT NULL
)
''')

cursor.execute('DROP TABLE IF EXISTS tax_details')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tax_details (
    uid TEXT PRIMARY KEY,
    afm INTEGER NOT NULL,
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
    FOREIGN KEY (afm) REFERENCES person(afm)
)
''')

conn.commit()
conn.close()
