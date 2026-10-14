import logging
import os
import uuid
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    afm TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS person (
    afm TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    family_status TEXT NOT NULL,
    children INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tax_details (
    uid TEXT PRIMARY KEY,
    afm TEXT NOT NULL REFERENCES person(afm),
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
    submission_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class PostgresManager:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")

    @contextmanager
    def _cursor(self):
        """Yield a cursor; commit if the block succeeds, roll back if it raises, and always close the connection."""
        conn = psycopg2.connect(self.database_url)
        try:
            with conn:  # transaction: commit on success, rollback on error
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    yield cursor
        finally:
            conn.close()

    def create_tables(self):
        with self._cursor() as cursor:
            cursor.execute(SCHEMA)

    def reset(self):
        """Drop all tables and recreate them empty."""
        with self._cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS tax_details, person, users")
        self.create_tables()

    def save_tax_data(self, tax_data) -> str:
        """Store the person's details and one tax submission in a single transaction."""
        uid = str(uuid.uuid4())
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO person (afm, name, address, family_status, children)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (afm) DO UPDATE SET
                    name=EXCLUDED.name,
                    address=EXCLUDED.address,
                    family_status=EXCLUDED.family_status,
                    children=EXCLUDED.children
                """,
                (tax_data.afm, tax_data.name, tax_data.address, tax_data.family_status, tax_data.children),
            )
            cursor.execute(
                """
                INSERT INTO tax_details (uid, afm, salary, freelance, rental, investments, business, medical,
                    donations, insurance, renovation, property_details, property_value, vehicles,
                    tax_prepayments, insurance_payments)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (uid, tax_data.afm, tax_data.salary, tax_data.freelance, tax_data.rental, tax_data.investments,
                 tax_data.business, tax_data.medical, tax_data.donations, tax_data.insurance,
                 tax_data.renovation, tax_data.property_details, tax_data.property_value, tax_data.vehicles,
                 tax_data.tax_prepayments, tax_data.insurance_payments),
            )
        logger.info("Saved tax submission %s", uid)
        return uid

    def get_person_data(self, afm: str):
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM person WHERE afm = %s", (afm,))
            row = cursor.fetchone()
        return dict(row) if row else None

    def get_tax_details(self, afm: str):
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM tax_details WHERE afm = %s ORDER BY submission_date DESC", (afm,))
            rows = cursor.fetchall()
        return [_jsonable(row) for row in rows]

    def get_submission(self, uid: str, afm: str):
        """Return one submission, only if it belongs to the given AFM."""
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM tax_details WHERE uid = %s AND afm = %s", (uid, afm))
            row = cursor.fetchone()
        return _jsonable(row) if row else None

    def add_user(self, afm: str, email: str, hashed_password: str):
        with self._cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (afm, email, password) VALUES (%s, %s, %s)", (afm, email, hashed_password)
            )

    def get_user_by_afm(self, afm: str):
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE afm = %s", (afm,))
            row = cursor.fetchone()
        return dict(row) if row else None

    def authenticate_user(self, afm: str, password: str):
        user = self.get_user_by_afm(afm)
        if user and pwd_context.verify(password, user["password"]):
            return user
        return None


def _jsonable(row) -> dict:
    data = dict(row)
    if data.get("submission_date") is not None:
        data["submission_date"] = data["submission_date"].strftime("%Y-%m-%d %H:%M:%S")
    return data
