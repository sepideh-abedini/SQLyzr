from typing import Optional, List, Tuple

from src.rel.db_facade import DatabaseFacade, DB_TIMEOUT, DB_CACHE
import mysql.connector
from loguru import logger

from src.util.db_cache import lookup_db_cache, save_db_cache
from src.util.str_utils import shrink_whitespaces, quote_str


class MysqlFacade(DatabaseFacade):

    def get_primary_key(self, db_id, table_name):
        query = f"SHOW KEYS FROM `{table_name}` WHERE Key_name = 'PRIMARY'"
        res = self.exec_query_sync(db_id, query)
        res = list(map(lambda r: r[4], res))
        return res

    def get_foreign_key(self, db_id, table_name):
        query = f"""SELECT COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                   FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                   WHERE TABLE_NAME = '{table_name}'
                   AND REFERENCED_TABLE_NAME IS NOT NULL;"""
        res = self.exec_query_sync(db_id, query)
        res = list(map(lambda r: f'({table_name}.{r[0]}, {r[2]}.{r[3]})', res))
        return res

    def get_col_names(self, db_id, table_name):
        query = f"SHOW COLUMNS FROM `{table_name}`"
        res = self.exec_query_sync(db_id, query)
        res = list(map(lambda r: r[0], res))
        return res

    def get_create_sql(self, db_id, table_name):
        query = f"SHOW CREATE TABLE `{table_name}`"
        res = self.exec_query_sync(db_id, query)
        res = res[0][1]
        res = shrink_whitespaces(res)
        return res

    def get_tables(self, db_id):
        res = self.exec_query_sync(db_id, "SHOW TABLES")
        return list(map(lambda r: r[0], res))

    def exec_query_uncached(self, db_id: str, sql: str, timeout: int = DB_TIMEOUT) -> Optional[List[Tuple]]:
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {db_id}")
            cursor.execute(sql)
            res = cursor.fetchall()
            return res
        except Exception as e:
            logger.error(e)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def get_connection(self):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sheep"
        )
        return connection

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
