import asyncio
import time
from typing import List, Dict, Tuple, Set

import tqdm
from oracledb import DatabaseError
from pydantic import BaseModel

from src.dataset.ora import OraClient
from src.util.file_utils import read_json

ORACLE_TO_MYSQL = {
    "VARCHAR2": "VARCHAR2(4000)",
    "CHAR": "VARCHAR2(4000)",
    "NUMBER": "NUMBER"
}

TABLES = dict()
DEPS = dict()


class BeaverTableSpec(BaseModel):
    db_id: str
    table_name_original: str
    column_names_original: List[str]
    column_types: List[str]

    @property
    def cols_spec(self):
        result = (",".join(
            f"{n} {ORACLE_TO_MYSQL.get(t.upper(), t.upper())}" for n, t in
            zip(self.column_names_original, self.column_types)
        ))
        return result

    @property
    def create_table_stmt(self):
        return f"CREATE TABLE {self.table_name_original} ({self.cols_spec})"


def gen_tables_sql(tables_path):
    lines = []
    tables = read_json(tables_path)
    table_names = set()

    for entry in tables:
        table_spec = BeaverTableSpec.model_validate(entry)
        table_names.add(table_spec.table_name_original)
        cols = set()
        for n, t in zip(table_spec.column_names_original, table_spec.column_types):
            cols.add(n)
            not_null = ("NOT NULL" in t)
        TABLES[table_spec.table_name_original] = set()
        DEPS[table_spec.table_name_original] = set()
        lines.append(table_spec.create_table_stmt)

    with open("data/beaver/dw/gen.sql", "w") as file:
        file.write(";\n\n".join(lines))

    return table_names


def gen_keys(keys_path):
    keys = read_json(keys_path)
    uniques = dict()
    fks = dict()
    for k1, k2 in keys:
        t1, c1 = k1.split(".")
        t2, c2 = k2.split(".")
        uniques[f"uq_{t2}_{c2}"] = f"ALTER TABLE {t2} ADD CONSTRAINT uq_{t2}_{c2} UNIQUE ({c2})"
        fks[f"fk_{t1}_{c1}"] = f"ALTER TABLE {t1} ADD CONSTRAINT fk_{t1}_{c1} FOREIGN KEY ({c1}) REFERENCES {t2}({c2})"

    with open("data/beaver/dw/fk.sql", "w") as file:
        file.write(";\n\n".join(uniques.values()))
        file.write(";\n\n")
        file.write(";\n\n".join(fks.values()))


def exec_queries(queries_path):
    queries = read_json(queries_path)
    lines = []
    for q in queries:
        sql = q['sql']
        lines.append(sql)

    with open("data/beaver/dw/queries.sql", "w") as file:
        file.write(";\n\n".join(lines))


def it(tables: Set[str], fks: Dict[Tuple[str, str], Tuple[str, str]]):
    deps = dict()
    for (t1, c1), (t2, c2) in fks.items():
        deps.setdefault(t1, set()).add(t2)
    ord_deps = []
    st = list(tables)
    while len(tables) > 0:
        print(len(st))
        t = st.pop(0)
        if deps.get(t, set()).issubset(set(ord_deps)):
            ord_deps.append(t)
        else:
            st.append(t)
        time.sleep(0.01)


async def optimize(tables_path, table_name):
    tables = read_json(tables_path)
    table_names = set()
    ora_client = OraClient()
    for entry in tables:
        table_spec = BeaverTableSpec.model_validate(entry)
        if table_spec.table_name_original == table_name:
            for col in tqdm.tqdm(table_spec.column_names_original):
                try:
                    await ora_client.exec(f"ALTER TABLE {table_name} MODIFY {col} VARCHAR2(10)")
                except DatabaseError as e:
                    print(e)
                    continue


async def main():
    # tables = gen_tables_sql("data/beaver/dw/dw.tables.json")
    # fks = gen_keys("data/beaver/dw/dw_join_keys.json")
    await optimize("data/beaver/dw/dw.tables.json", "SUBJECT_OFFERED")


# exec_queries("data/beaver/dw.dev.json")
# it(tables, fks)


if __name__ == '__main__':
    asyncio.run(main())
