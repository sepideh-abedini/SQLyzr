import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Set

from experimental.dscaler.sqlite_db import SqliteDatabase
from experimental.dscaler.sqlite_schema import SqliteColumn

MAX_COL_VALS = 100


@dataclass
class SqliteForeignKeyRefs:
    src_table: str
    src_col: str
    dst_table: str
    dst_col: str


@dataclass
class SqliteIndex:
    name: str
    unique: bool


class SqliteInterface:
    db: SqliteDatabase

    def __init__(self, db):
        self.db = db

    def get_tables(self, db_id: str):
        result = self.exec_query(db_id, "SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [_[0] for _ in result]
        return table_names

    def get_col_names(self, db_id, table_name):
        res = self.exec_query(db_id, f'PRAGMA table_info("{table_name}")')
        col_names = [_[1] for _ in res]
        return col_names

    def get_cols(self, db_id, table_name) -> Dict[str, SqliteColumn]:
        res = self.exec_query(db_id, f'PRAGMA table_info("{table_name}")')
        cols = {_[1]: SqliteColumn(table_name, _[1], _[2], _[5]) for _ in res}
        return cols

    def get_foreign_key(self, db_id, table_name) -> List[SqliteForeignKeyRefs]:
        res_raw = self.exec_query(db_id, f'PRAGMA foreign_key_list("{table_name}")')
        res = []
        for row in res_raw:
            table, src, dst = row[2:5]
            refs = SqliteForeignKeyRefs(src_table=table_name, src_col=src, dst_table=table, dst_col=dst)
            res.append(refs)
        return res

    def get_indexes(self, db_id: str, table) -> List[SqliteIndex]:
        result = self.exec_query(db_id, f"PRAGMA index_list({table})")
        result = list(map(lambda r: SqliteIndex(r[1], r[2]), result))
        return result

    def get_index_cols(self, db_id, index_name: str) -> Set[str]:
        result = self.exec_query(db_id, f"PRAGMA index_info({index_name})")
        cols = set(map(lambda r: r[2], result))
        return cols

    def get_col_vals(self, db_id, table, col, limit: Optional[int] = MAX_COL_VALS) -> Set:
        if limit is None:
            res = self.exec_query(db_id, f'SELECT DISTINCT {col} FROM {table}')
        else:
            res = self.exec_query(db_id, f'SELECT DISTINCT {col} FROM {table} LIMIT {MAX_COL_VALS}')
        vals = set(map(lambda r: r[0], res))
        return vals

    def get_col_list_vals(self, db_id, table, cols: List[str]) -> Set[Tuple]:
        cols_str = ", ".join(cols)
        res = self.exec_query(db_id, f'SELECT DISTINCT {cols_str} FROM {table}')
        vals = set(map(lambda r: tuple(r), res))
        return vals

    def get_primary_key(self, db_id, table_name):
        res_raw = self.exec_query(db_id, f'PRAGMA table_info("{table_name}");')
        pks = list()
        for row in res_raw:
            if row[5] == 1:
                pks.append(row[1])
        return pks

    def get_num_rows(self, db_id, table_name):
        res = self.exec_query(db_id, f"SELECT COUNT(*) FROM {table_name}")
        return res[0][0]

    def exec_query(self, db_id: str, sql: str) -> Optional[List[Tuple]]:
        conn = sqlite3.connect(f"file:{self.db.get_db_path(db_id)}?mode=rw", timeout=10)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            conn.commit()
        except Exception as e:
            print(e)
            rows = None
        finally:
            cursor.close()
            conn.close()
        return rows
