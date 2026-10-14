"""Create the database tables (the app also does this on start-up).

    python database.py           create any missing tables
    python database.py --reset   drop all tables and recreate them empty
"""
import sys

from dotenv import load_dotenv

from postgres_manager import PostgresManager

if __name__ == "__main__":
    load_dotenv()
    manager = PostgresManager()
    if "--reset" in sys.argv:
        manager.reset()
        print("Database reset.")
    else:
        manager.create_tables()
        print("Tables created.")
