import os
import psycopg2
import psycopg2.extras
import uuid
import logging
from passlib.context import CryptContext
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PostgresManager:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL")
        logging.info("Initialized PostgresManager with database URL.")

    def _connect(self):
        logging.debug("Establishing a new database connection.")
        return psycopg2.connect(self.database_url)

    def upload_person(self, tax_data):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            logging.debug("Uploading person data to database.")
            cursor.execute('''
            INSERT INTO person (afm, name, address, family_status, children)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (afm) DO UPDATE SET
                name=EXCLUDED.name,
                address=EXCLUDED.address,
                family_status=EXCLUDED.family_status,
                children=EXCLUDED.children
            ''', (tax_data.afm, tax_data.name, tax_data.address, tax_data.family_status, tax_data.children))
            conn.commit()
            cursor.close()
            conn.close()
            logging.info(f"Uploaded to person table: {tax_data}")
        except Exception as e:
            logging.error(f"Error uploading to person table: {e}")

    def upload_tax_details(self, uid, tax_data):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            logging.debug("Uploading tax details to database.")
            cursor.execute('''
            INSERT INTO tax_details (uid, afm, salary, freelance, rental, investments, business, medical, donations, insurance, renovation, property_details, property_value, vehicles, tax_prepayments, insurance_payments)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (uid, tax_data.afm, tax_data.salary, tax_data.freelance, tax_data.rental, tax_data.investments, tax_data.business, tax_data.medical, tax_data.donations, tax_data.insurance, tax_data.renovation, tax_data.property_details, tax_data.property_value, tax_data.vehicles, tax_data.tax_prepayments, tax_data.insurance_payments))
            conn.commit()
            cursor.close()
            conn.close()
            logging.info(f"Uploaded to tax_details table: {uid}, {tax_data}")
        except Exception as e:
            logging.error(f"Error uploading to tax details table: {e}")

    def save_tax_data(self, tax_data):
        uid = str(uuid.uuid4())
        logging.debug("Generated new UUID for tax data.")
        self.upload_person(tax_data)
        self.upload_tax_details(uid, tax_data)
        logging.info("Saved tax data.")
        return uid

    def get_person_data(self, afm: str):
        try:
            conn = self._connect()
            conn.autocommit = True
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            logging.debug(f"Fetching person data for AFM: {afm}.")
            cursor.execute('SELECT * FROM person WHERE afm = %s', (afm,))
            person_data = cursor.fetchone()
            cursor.close()
            conn.close()

            if not person_data:
                logging.warning(f"No person data found for AFM: {afm}.")
                return None

            logging.info(f"Fetched person data for AFM: {afm}.")
            return dict(person_data)
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def get_tax_details(self, afm: str):
        try:
            conn = self._connect()
            conn.autocommit = True
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            logging.debug(f"Fetching tax details for AFM: {afm}.")
            cursor.execute('SELECT * FROM tax_details WHERE afm = %s ORDER BY submission_date DESC', (afm,))
            tax_details_data = cursor.fetchall()
            cursor.close()
            conn.close()

            logging.info(f"Fetched tax details for AFM: {afm}.")
            return [dict(row) for row in tax_details_data]
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def add_user(self, afm: str, email: str, password: str):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            logging.debug(f"Adding new user with AFM: {afm}.")
            cursor.execute(
                "INSERT INTO users (afm, email, password) VALUES (%s, %s, %s)",
                (afm, email, password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            logging.info(f"Added new user with AFM: {afm}.")
        except Exception as e:
            logging.error(f"Error adding user: {e}")

    def get_user_by_afm(self, afm):
        try:
            conn = self._connect()
            conn.autocommit = True
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            logging.debug(f"Fetching user data for AFM: {afm}.")
            cursor.execute("SELECT * FROM users WHERE afm = %s", (afm,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            logging.info(f"Fetched user data for AFM: {afm}.")
            return dict(user) if user else None
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            raise Exception(f"Database error: {e}")

    def authenticate_user(self, afm, password):
        logging.debug(f"Authenticating user with AFM: {afm}.")
        user = self.get_user_by_afm(afm)
        if user and pwd_context.verify(password, user["password"]):
            logging.info(f"User authenticated successfully for AFM: {afm}.")
            return user
        else:
            logging.warning(f"Authentication failed for AFM: {afm}.")
            return None
