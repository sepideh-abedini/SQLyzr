import asyncio
import csv
import os
import subprocess
import time
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import List, Dict

import oracledb.exceptions
import tqdm
from tqdm.asyncio import tqdm as atqdm
from pydantic import BaseModel

from src.dataset.ora import exec_ora, OraClient
from src.util.file_utils import read_json


def chunk_list(lst, num_chunks=10):
    chunk_size = len(lst) // num_chunks + (len(lst) % num_chunks > 0)
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


@dataclass
class InsertStmt:
    table_name: str
    cols: List[str]
    val_strs: List[str] = field(default_factory=list)

    def add_vals(self, vals: List[str]):
        vs = []
        for c, v in zip(self.cols, vals):
            # if v.strip() == '':
            #     vs.append('NULL')
            # else:
            v = v.replace("'", "''")
            vs.append(f"'{v}'")
        self.val_strs.append(f"({','.join(vs)})")

    def str(self):
        cs = list(map(lambda c: f"{c}", self.cols))
        # return f"INSERT INTO {self.table_name} ({','.join(cs)}) VALUES {','.join(self.val_strs)}"
        return f"INSERT INTO {self.table_name} ({','.join(cs)}) VALUES ({','.join([f':{i}' for i in range(len(self.cols))])})"


def count_lines_wc(file_path):
    return int(subprocess.check_output(['wc', '-l', file_path]).split()[0])


async def add_data(table_name):
    if table_name != "FCLT_ROOMS_HIST":
        return
    table_path = f"data/beaver/dw/csv/{table_name}.csv"
    sql_path = f"data/beaver/dw/sql/{table_name}.sql"
    ora_client = OraClient()
    sqls = []
    num_tup = await ora_client.exec(f"SELECT count(*) FROM {table_name}")
    num_tup = num_tup[0][0]
    num_rows = count_lines_wc(table_path) - 1
    print(f"Existing tuples {table_name}: {num_tup}")
    print(f"Num rows[{table_name}]::{num_rows}")
    if num_rows == 0:
        return
    if num_rows == num_tup:
        print(f"Table already populated, skipping: {table_name}")
        return
    try:
        with open(table_path) as file:
            reader = csv.reader(file)
            cols = next(reader)
            rows = list(islice(reader, 3_750_000))
            # rows = list(reader)
            CHUNK_TOTAL_SIZE = 300_000
            row_size = len(" ".join(rows[0]))
            print(f"{table_name}: row size: {row_size}")
            rows_per_chunk = max(1, CHUNK_TOTAL_SIZE // row_size)
            print(f"{table_name}: rows per chunk: {rows_per_chunk}")
            await ora_client.exec(f"DELETE FROM {table_name}")
            num_tup = await ora_client.exec(f"SELECT count(*) FROM {table_name}")
            print(f"Table: {table_name}, rows after drop: {num_tup}")
            num_chunk = max(1, len(rows) // rows_per_chunk)
            rows_chunks = chunk_list(rows, num_chunk)
            sqls = []
            c = 0
            tasks =[]
            for chunk in tqdm.tqdm(rows_chunks):
                stmt = InsertStmt(table_name, cols)
                params = []
                for row in chunk:
                    params.append(tuple(row))
                    c += 1
                    # stmt.add_vals(row)
                tasks.append(ora_client.exec_many(stmt.str(), params))
                # if len(chunk) > 0:
                #     sqls.append(stmt.str())
            await atqdm.gather(*tasks)
            print(c)
            # await ora_client.exec_batch(sqls)
            # await ora_client.exec_many(stmt.str(), params_list)
    except Exception as e:
        print(e)
        print(f"FAILED TABLE: {table_name}")
    num_tup = await ora_client.exec(f"SELECT COUNT(*) FROM {table_name}")
    print(f"Table: {table_name}, rows after insertion: {num_tup}")
    await ora_client.close()
    # with open(sql_path, "w") as file:
    #     file.write(";\n\n".join(sqls))


def gen_data():
    files = os.listdir("data/beaver/dw/csv")
    tables = set()
    for file in tqdm.tqdm(files):
        if "csv" in file:
            table_name = Path(file).stem
            add_data(table_name)
            tables.add(table_name)
    #         sql = get_sql(table_name)
    #         if sql:
    #             inserts[table_name] = sql


def exec_data():
    files = os.listdir("data/beaver/dw/sql")
    tables = set()
    failed_tables = set()
    for file in tqdm.tqdm(files, leave=False, position=0):
        if "sql" in file:
            table_name = Path(file).stem
            exec_ora(f"DELETE FROM {table_name}")
            with open(os.path.join("data/beaver/dw/sql", file)) as f:
                script = f.read()
                commands = script.split(";\n\n")
                for cmd in tqdm.tqdm(commands, leave=False, desc=table_name, position=1):
                    try:
                        exec_ora(cmd)
                    except Exception as e:
                        print(e)
                        print("Failed table: ", table_name)
                        failed_tables.add(table_name)
                        break
    print("Failed tables:", failed_tables)
    # add_data(table_name)
    # tables.add(table_name)
    #         sql = get_sql(table_name)
    #         if sql:
    #             inserts[table_name] = sql


async def main():
    files = os.listdir("data/beaver/dw/sql")
    for file in files:
        table_name = Path(file).stem
        await add_data(table_name)
        # await add_data("SUBJECT_IAP_SCHEDULE")


if __name__ == '__main__':
    asyncio.run(main())
