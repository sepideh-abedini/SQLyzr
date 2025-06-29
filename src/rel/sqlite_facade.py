import sqlite3
import time
from contextlib import contextmanager
from sqlite3 import Connection
from typing import Optional, List, Tuple

from loguru import logger

from src.eval.dataset_config import DatasetConfig
from src.rel.db_facade import DatabaseFacade, DB_TIMEOUT, DB_CACHE
from src.util.db_cache import save_db_cache, lookup_db_cache
from src.util.str_utils import shrink_whitespaces


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
    def check_connection(self):
        logger.info("Checking SQLite connection!")

    def get_schema_str(self, db_id):
        tables_str = []
        for table in self.get_tables(db_id):
            tables_str.append(self.get_table_schema_str(db_id, table))
        return "\n".join(tables_str)

    def get_table_schema_str(self, db_id, table):
        schema_str = ""
        create_sql = self.get_create_sql(db_id, table)
        cols = self.get_col_names(db_id, table)
        cols_str = "\t".join(cols)
        sample_rows = self.exec_query_sync(db_id, f"SELECT * FROM {table} LIMIT 3")
        if sample_rows:
            rows_str = "\n".join(map(lambda r: "\t".join(list(map(lambda cv: str(cv)[:50], r))), sample_rows))
        else:
            rows_str = "\n"
        schema_str += f"\n {create_sql}\n"
        schema_str += f"\n/*\n3 rows from {table}:\n{cols_str}\n{rows_str}\n*/\n"
        return schema_str

    def get_create_sql(self, db_id, table_name):
        query = f"SELECT sql FROM sqlite_master WHERE tbl_name='{table_name}'"
        result = self.exec_query_sync(db_id, query)
        result = result[0][0]
        result = shrink_whitespaces(result)
        return result

    def get_col_names(self, db_id, table_name):
        res = self.exec_query_sync(db_id, f'PRAGMA table_info("{table_name}")')
        col_names = [_[1] for _ in res]
        return col_names

    def get_foreign_key(self, db_id, table_name):
        res_raw = self.exec_query_sync(db_id, f'PRAGMA foreign_key_list("{table_name}")')
        res_clean = list()
        for row in res_raw:
            table, source, to = row[2:5]
            row_clean = f"({table_name}.{source}, {table}.{to})"
            res_clean.append(row_clean)
        return res_clean

    def get_primary_key(self, db_id, table_name):
        res_raw = self.exec_query_sync(db_id, f'PRAGMA table_info("{table_name}");')
        pks = list()
        for row in res_raw:
            if row[5] == 1:
                pks.append(row[1])
        return pks

    def get_tables(self, db_id: str):
        result = self.exec_query_sync(db_id, "SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [_[0] for _ in result]
        return table_names

    def __init__(self, conf: DatasetConfig):
        super().__init__(conf)

    def exec_query_uncached(self, db_id: str, sql: str, timeout: int = DB_TIMEOUT) -> Optional[List[Tuple]]:

        db_file = self.conf.get_db_file_path(db_id)
        try:
            conn = sqlite3.connect(f"file:{db_file}?mode=ro")
        except sqlite3.OperationalError as e:
            if "unable to open database file" in str(e):
                logger.error(f"SQLite Error: {db_id} {db_file}")
            else:
                logger.error(f"SQLite Error: {db_id} {sql}")
            raise
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
                    logger.warning(f"SQLite Timed out: {db_id} {sql}")
                else:
                    logger.error(f"SQLite Error: {e}")
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
