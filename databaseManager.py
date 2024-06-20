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

    def get_person_data(self, afm: str):
        try:
            conn = sqlite3.connect(self.dbname)
            conn.row_factory = sqlite3.Row  # This enables the row_factory to return dict-like objects
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM person WHERE afm = ?', (afm,))
            person_data = cursor.fetchone()
            conn.close()

            if not person_data:
                return None

            return dict(person_data)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def get_tax_details(self, afm: str):
        try:
            conn = sqlite3.connect(self.dbname)
            conn.row_factory = sqlite3.Row  # This enables the row_factory to return dict-like objects
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM tax_details WHERE afm = ? ORDER BY submission_date DESC', (afm,))
            tax_details_data = cursor.fetchall()
            conn.close()

            return [dict(row) for row in tax_details_data]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def save_user(self, afm, email, password):
        try:
            conn = sqlite3.connect(self.dbname)
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (afm, email, password)
            VALUES (?, ?, ?)
            ''', (afm, email, password))
            conn.commit()
            conn.close()
            print(f"User {afm} registered successfully.")
        except sqlite3.IntegrityError:
            raise
        except Exception as e:
            print(f"Error saving user: {e}")
            raise

    def get_user(self, afm):
        try:
            conn = sqlite3.connect(self.dbname)
            conn.row_factory = sqlite3.Row  # This enables the row_factory to return dict-like objects
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE afm = ?', (afm,))
            user_data = cursor.fetchone()
            conn.close()

            if not user_data:
                return None

            return dict(user_data)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
