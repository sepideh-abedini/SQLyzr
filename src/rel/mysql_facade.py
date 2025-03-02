from typing import Optional, List, Tuple

from src.rel.db_facade import DatabaseFacade, DB_TIMEOUT, DB_CACHE
from mysql.connector import pooling
from loguru import logger

from src.util.db_cache import lookup_db_cache, save_db_cache

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host="localhost",
    user="root",
    password="sheep"
)


class MysqlFacade(DatabaseFacade):
    def exec_query_uncached(self, db_id: str, sql: str, timeout: int = DB_TIMEOUT) -> Optional[List[Tuple]]:
        conn = None
        cursor = None
        try:
            conn = pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {db_id}")
            cursor.execute(sql)
            res = cursor.fetchall()
            return res
        except Exception as e:
            logger.error(e)
        finally:
            if conn:
                cursor.close()
            if cursor:
                conn.close()

    def exec_query_sync(self, db_id: str, sql: str, timeout: int = DB_TIMEOUT) -> Optional[List[Tuple]]:
        if DB_CACHE:
            res = lookup_db_cache(db_id, sql)
            if res:
                logger.debug("Cache hit")
                return res
        result = self.exec_query_uncached(db_id, sql, timeout)
        if DB_CACHE:
            save_db_cache(db_id, sql, result)
        return result
