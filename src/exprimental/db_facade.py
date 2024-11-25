import sqlite3
from os import path
from typing import List, Tuple


class DatabaseFacade:
    dbs_dir: str

    def __init__(self, dbs_dir):
        self.dbs_dir = dbs_dir

    def get_db_path(self, db_name: str):
        return path.join(self.dbs_dir, db_name, f"{db_name}.sqlite")

    def execute_query(self, db_id: str, sql: str) -> List[Tuple]:
        connection = sqlite3.connect(self.get_db_path(db_id))
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            rows = None
        cursor.close()
        connection.close()
        return rows
