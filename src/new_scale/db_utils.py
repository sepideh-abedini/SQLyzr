import sqlite3
from datetime import datetime


def get_total_row_count(db_path):
    total_rows = 0
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get the names of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table_name in tables:
            name = table_name[0]
            # Use f-string carefully; table names are internal here
            cursor.execute(f"SELECT COUNT(*) FROM {name}")
            count = cursor.fetchone()[0]
            total_rows += count

        conn.close()
        return total_rows

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


class Timer:
    start_time: datetime

    def __init__(self):
        self.start_time = datetime.now()

    @staticmethod
    def start():
        return Timer()

    def lap(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()
