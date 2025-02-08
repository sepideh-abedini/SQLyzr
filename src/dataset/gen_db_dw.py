import asyncio
import csv
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict
from tqdm.asyncio import tqdm

import aiomysql
from pydantic import BaseModel
from tqdm.asyncio import tqdm

from src.configs.datasets import BEAVER_DEV
from src.util.file_utils import read_json


@dataclass
class SchemaCol:
    not_null: bool


class SchemaTable:
    cols: Dict[str, SchemaCol]

    def __init__(self):
        self.cols = dict()


class SchemaDB:
    tables: Dict[str, SchemaTable]

    def __init__(self):
        self.tables = dict()


class BeaverSchema:
    dbs: Dict[str, SchemaDB]

    def __init__(self):
        self.dbs = dict()


class BeaverTableSpec(BaseModel):
    db_id: str
    table_name_original: str
    column_names_original: List[str]
    column_types: List[str]

    @property
    def create_db_stmt(self):
        return f"CREATE DATABASE IF NOT EXISTS {self.db_id}"

    @property
    def cols_spec(self):
        result = (",".join(
            f"`{n}` {ORACLE_TO_MYSQL.get(t.upper(), t.upper())}" for n, t in
            zip(self.column_names_original, self.column_types)
        ))
        return result

    @property
    def drop_table_stmt(self):
        return f"DROP TABLE IF EXISTS {self.table_name_original}"

    @property
    def create_table_stmt(self):
        return f"CREATE TABLE IF NOT EXISTS `{self.table_name_original}` ({self.cols_spec})"


async def exec_stmt(stmt: str, db=None):
    # connection = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password=os.getenv("MYSQL_ROOT_PASSWORD"),
    #     db=db
    # )

    connection = await aiomysql.connect(
        host="localhost",
        user=os.getenv("MYSQL_USERNAME"),
        password=os.getenv("MYSQL_PASSWORD"),
        db=db,
        connect_timeout=1000
    )
    cursor = await connection.cursor()
    try:
        # Execute the SQL query
        await cursor.execute(stmt)
    except Exception as err:
        print(f"USE {db};")
        print(f"Error: {err}")
        print(stmt)
        raise err
    finally:
        await cursor.close()
        connection.close()


@dataclass
class InsertStmt:
    db_name: str
    table_name: str
    cols: List[str]
    val_strs: List[str] = field(default_factory=list)

    def add_vals(self, vals: List[str], schema: BeaverSchema):
        vs = []
        for c, v in zip(self.cols, vals):
            if v.strip() == '' and not schema.dbs[self.db_name].tables[self.table_name].cols[c].not_null:
                vs.append('NULL')
            else:
                vs.append(f"'{v}'")
        self.val_strs.append(f"({','.join(vs)})")

    def str(self):
        cs = list(map(lambda c: f"`{c}`", self.cols))
        return f"INSERT INTO `{self.table_name}` ({','.join(cs)}) VALUES {','.join(self.val_strs)}"


async def create_tables(tables_path):
    tables = read_json(tables_path)
    dbs = set(map(lambda t: t['db_id'], tables))
    schema = BeaverSchema()
    for db in dbs:
        stmt = f"DROP DATABASE IF EXISTS {db}"
        await exec_stmt(stmt)
        stmt = f"CREATE DATABASE {db}"
        await exec_stmt(stmt)
        schema.dbs[db] = SchemaDB()

    count = 0
    for entry in tables:
        table_spec = BeaverTableSpec.model_validate(entry)
        ta = SchemaTable()
        for n, t in zip(table_spec.column_names_original, table_spec.column_types):
            not_null = ("NOT NULL" in t)
            ta.cols[n] = SchemaCol(not_null)
        schema.dbs[table_spec.db_id].tables[table_spec.table_name_original] = ta
        await exec_stmt(table_spec.create_table_stmt, db=table_spec.db_id)
    return schema


dbs = ["csail_stata_cinder", "csail_stata_glance", "csail_stata_neutron", "csail_stata_nova", "keystone"]


def chunk_list(lst, num_chunks=10):
    chunk_size = len(lst) // num_chunks + (len(lst) % num_chunks > 0)
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def add_data(db_name, schema: BeaverSchema):
    db_path = f"data/beaver/download/drive/csv/{db_name}"
    for f in Path(db_path).iterdir():
        table = f.stem.lower()
        with open(f) as file:
            reader = csv.reader(file)
            cols = next(reader)
            rows = list(reader)
            print(f"Num rows: {table}::{len(rows)}")
            if len(rows) == 0:
                continue
            # rows = rows[:min(100000, len(rows))]
            rows_chunks = chunk_list(rows, 50)
            tasks = []
            for chunk in rows_chunks:
                stmt = InsertStmt(db_name, table, cols)
                for row in chunk:
                    stmt.add_vals(row, schema)
                sql = stmt.str()
                try:
                    await exec_stmt(sql, db=db_name)
                    # tasks.append(exec_stmt(sql, db=db_name))
                except Exception as e:
                    raise e
            # await tqdm.gather(*tasks, total=len(tasks))
        print(f"Completed {f.stem}")


async def setup_db():
    schema = await create_tables("data/beaver/dw.tables.json")
    # for db in dbs:
    #     await add_data(db, schema)


async def main():
    await setup_db()
    # schema = await create_tables()
    # for db in dbs:
    #     await add_data(db, schema)


if __name__ == '__main__':
    asyncio.run(main())
