import sqlite3
import uuid

class SqliteManager:
    def __init__(self) -> None:
        self.dbname = "tax_database.db"

    def upload_person(self, tax_data):
        try:
            conn = sqlite3.connect(self.dbname)
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO person (afm, name, address, family_status, children)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(afm) DO UPDATE SET
                name=excluded.name,
                address=excluded.address,
                family_status=excluded.family_status,
                children=excluded.children
            ''', (tax_data.afm, tax_data.name, tax_data.address, tax_data.family_status, tax_data.children))
            conn.commit()
            conn.close()
            print(f"Uploaded to person table: {tax_data}")
        except Exception as e:
            print(f"Error uploading to person table: {e}")

    def upload_tax_details(self, uid, tax_data):
        try:
            conn = sqlite3.connect(self.dbname)
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO tax_details (uid, afm, salary, freelance, rental, investments, business, medical, donations, insurance, renovation, property_details, property_value, vehicles, tax_prepayments, insurance_payments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (uid, tax_data.afm, tax_data.salary, tax_data.freelance, tax_data.rental, tax_data.investments, tax_data.business, tax_data.medical, tax_data.donations, tax_data.insurance, tax_data.renovation, tax_data.property_details, tax_data.property_value, tax_data.vehicles, tax_data.tax_prepayments, tax_data.insurance_payments))
            conn.commit()
            conn.close()
            print(f"Uploaded to tax_details table: {uid}, {tax_data}")
        except Exception as e:
            print(f"Error uploading to tax details table: {e}")

    def save_tax_data(self, tax_data):
        uid = str(uuid.uuid4())
        self.upload_person(tax_data)
        self.upload_tax_details(uid, tax_data)
        return uid