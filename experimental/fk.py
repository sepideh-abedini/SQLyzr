import asyncio
import json

import tqdm

from src.configs.datasets import BIRD_ALL
from src.rel.db_factory import DatabaseFactory

db_facade = DatabaseFactory.get_instance(BIRD_ALL)


def get_num_rows(db_id, table):
    sql = f"SELECT Count(*) FROM '{table}'"
    res = db_facade.exec_query_sync(db_id, sql)
    return int(res[0][0])


def get_tables(db_id):
    sql = "SELECT name FROM sqlite_master WHERE type='table';"
    res = db_facade.exec_query_sync(db_id, sql)
    return list(map(lambda t: t[0], res))


def get_fks(db_id, table):
    sql = f"PRAGMA foreign_key_list('{table}');"
    res = db_facade.exec_query_sync(db_id, sql)
    return list(map(lambda t: t[3], res))


async def main():
    with open(BIRD_ALL.get_tables_path()) as f:
        data = json.load(f)

    dbs = dict()
    for e in tqdm.tqdm(data, total=len(data)):
        tables = set()
        db_id = e["db_id"]
        valid_tables = get_tables(db_id)
        for t in e['table_names']:
            if t not in valid_tables:
                print(f"Table not exists in actual db: {db_id}:{t}")
            else:
                tables.add(t)
        dbs[db_id] = tables

    fks_stmts = []
    for db_id, tables in tqdm.tqdm(dbs.items(), total=len(dbs.items())):
        for table in tqdm.tqdm(tables, total=len(tables), desc=f"{db_id}"):
            print(f"{db_id}:{table}")
            fks = get_fks(db_id, table)
            for fk in fks:
                stmt = f"CREATE INDEX fk_{db_id}_{table}_{fk} ON '{table}' ('{fk}')"
                fks_stmts.append(stmt)
                db_facade.exec_query_sync(db_id, stmt)
    # with open("fks_ids.sql", "w") as file:
    #     for stmt in fks_stmts:
    #         file.write(f"{stmt}\n")


if __name__ == '__main__':
    asyncio.run(main())
