import os
import sqlite3
from functools import lru_cache, cache
from os import path
from typing import List, Tuple

import aiosqlite
from loguru import logger


class DatabaseFacade:
    dbs_dir: str

    def __init__(self, dbs_dir):
        self.dbs_dir = dbs_dir

    def get_db_path(self, db_name: str):
        return path.join(self.dbs_dir, db_name, f"{db_name}.sqlite")

    @cache
    def exec_query_sync(self, db_id: str, sql: str) -> List[Tuple]:
        connection = sqlite3.connect(self.get_db_path(db_id))
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
            rows = None
        cursor.close()
        connection.close()
        return rows

    # FIXME: Use cache
    async def exec_query_async(self, db_id: str, sql: str) -> List[Tuple]:
        db = None
        cursor = None

        if not os.path.exists(self.get_db_path(db_id)):
            raise RuntimeError(f"Database file not exists {self.get_db_path(db_id)}")
        try:
            db = await aiosqlite.connect(self.get_db_path(db_id))
            cursor = await db.execute(sql)
            rows = await cursor.fetchall()
            return rows
        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
            print(e)
            logger.debug(e)
            return None
        finally:
            if cursor:
                await cursor.close()
            if db:
                await db.close()
