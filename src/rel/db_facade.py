import os
import sqlite3
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from sqlite3 import Connection
from typing import List, Tuple, Optional

from src.util.db_cache import lookup_db_cache, save_db_cache
from loguru import logger

from src.eval.dataset_config import DatasetConfig

IN_MEM_DB = False

DB_TIMEOUT = int(os.environ.get("DB_TIMEOUT", 60_000))
DB_CACHE = bool(int(os.environ.get("DB_CACHE", 0)))


class DatabaseFacade(ABC):
    conf: DatasetConfig

    def __init__(self, conf: DatasetConfig):
        self.conf = conf

    @abstractmethod
    def exec_query_sync(self, db_id: str, sql: str, timeout: int = DB_TIMEOUT) -> Optional[List[Tuple]]:
        pass


@contextmanager
def sqlite_timelimit(conn: Connection, ms):
    # logger.trace(f"[{os.getpid()}]: Still Executing query!!")
    deadline = time.perf_counter() + (ms / 1000)
    n = 1000
    if ms <= 20:
        n = 1

    def handler():
        if time.perf_counter() >= deadline:
            return 1

    conn.set_progress_handler(handler, n)
    try:
        yield
    finally:
        conn.set_progress_handler(None, n)
        conn.close()


class SqliteFacade(DatabaseFacade):

    def __init__(self, conf: DatasetConfig):
        super().__init__(conf)

    def exec_query_uncached(self, db_id: str, sql: str, timeout: int = DB_TIMEOUT) -> Optional[List[Tuple]]:
        conn = sqlite3.connect(f"file:{self.conf.get_db_file_path(db_id)}?mode=ro")
        logger.debug(f"Connection created")

        with sqlite_timelimit(conn, DB_TIMEOUT):
            cursor = conn.cursor()
            try:
                cursor.execute(sql)
                logger.debug(f"Query executed")

                rows = cursor.fetchall()
                logger.debug(f"Result fetched")
            except Exception as e:
                if e.args == ('interrupted',):
                    if DB_CACHE:
                        save_db_cache(db_id, sql, None)
                    logger.debug(f"SQLite Timed out: {db_id} {sql}")
                else:
                    logger.debug(e)
                rows = None
            finally:
                cursor.close()
            return rows

    def exec_query_sync(self, db_id: str, sql: str, timeout: int = DB_TIMEOUT) -> Optional[List[Tuple]]:
        if DB_CACHE:
            res = lookup_db_cache(db_id, sql)
            if res:
                logger.trace("Cache hit")
                return res

        result = self.exec_query_uncached(db_id, sql, timeout)

        if DB_CACHE:
            save_db_cache(db_id, sql, result)
        return result
