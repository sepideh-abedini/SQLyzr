import asyncio
import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

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
    primary_key: List[str]

    @property
    def create_db_stmt(self):
        return f"CREATE DATABASE IF NOT EXISTS {self.db_id}"

    @property
    def cols_spec(self):
        for n, t in zip(self.column_names_original, self.column_types):
            if "AUTO_INCREMENT" in t:
                self.primary_key.remove(n)
                self.primary_key.insert(0, n)
        result = (",".join(
            f"`{n}` {t.upper()}" for n, t in
            zip(self.column_names_original, self.column_types)
        ))
        if len(self.primary_key) > 0:
            result += f", PRIMARY KEY ({','.join([f'`{k}`' for k in self.primary_key])})"
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
        db=db
    )
    cursor = await connection.cursor()
    try:
        # Execute the SQL query
        await cursor.execute(stmt)
    except Exception as err:
        print(f"USE {db};")
        print(stmt)
        # print(f"Error: {err}")
        raise err
    finally:
        await cursor.close()
        connection.close()


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
        db=db
    )
    cursor = await connection.cursor()
    try:
        # Execute the SQL query
        await cursor.execute(stmt)
    except Exception as err:
        print(f"USE {db};")
        print(stmt)
        # print(f"Error: {err}")
        raise err
    finally:
        await cursor.close()
        connection.close()


@dataclass
class InsertStmt:
    db_name: str
    table_name: str
    cols: List[str]

    def str(self, vals: List[str], schema: BeaverSchema):
        cs = []
        vs = []
        for c, v in zip(self.cols, vals):
            cs.append(f"`{c}`")
            if v.strip() == '' and not schema.dbs[self.db_name].tables[self.table_name].cols[c].not_null:
                vs.append('NULL')
            else:
                vs.append(f"'{v}'")

        return f"INSERT INTO `{self.table_name}` ({','.join(cs)}) VALUES ({','.join(vs)})"


async def create_tables():
    conf = BEAVER_DEV
    tables = read_json(conf.get_tables_path())
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


async def add_data(db_name, schema: BeaverSchema):
    db_path = f"data/beaver/download/drive/csv/{db_name}"
    for f in Path(db_path).iterdir():
        table = f.stem.lower()
        with open(f) as file:
            reader = csv.reader(file)
            cols = next(reader)
            rows = list(reader)
            rows = rows[:min(10, len(rows))]
            stmt = InsertStmt(db_name, table, cols)
            tasks = []
            for row in tqdm(rows, desc=f"Adding data for {db_name}:{table}", total=len(rows)):
                try:
                    await exec_stmt(stmt.str(row, schema), db=db_name)
                except Exception as e:
                    raise e


async def main():
    schema = await create_tables()
    for db in dbs:
        await add_data(db, schema)


# data = BeaverTableSpec.model_validate(entry)
# print(data.db_id)

if __name__ == '__main__':
    asyncio.run(main())
