import os.path
import sqlite3
from dataclasses import dataclass
from typing import List, Optional

from sdv.metadata import Metadata


def get_sd_stype(t: str):
    t = t.lower()
    if "varchar" in t:
        return "categorical"
    if "char" in t:
        return "categorical"
    if "datetime" in t:
        return "date"
    if t in {"text", "blob", "boolean", "bool"}:
        return "categorical"
    if t in {"datetime", "date", "timestamp"}:
        return "date"
    if t in {"int", "bit", "float", "double", "numeric", "year", "decimal", "real", "number", "integer"}:
        return "numerical"
    if "number" in t:
        return "numerical"
    if "numeric" in t:
        return "numerical"
    if "decimal" in t:
        return "numerical"
    if "int" in t:
        return "numerical"
    if "float" in t:
        return "numerical"
    if t == '':
        return "categorical"
    raise RuntimeError(f"Invalid type: {t}")


@dataclass
class ColDeclr:
    table: str
    name: str
    type: str
    pk: bool = False


@dataclass
class FKDeclr:
    src_table: str
    dst_table: str
    src: str
    dst: Optional[str]


def exec_sql(file, sql):
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    res = cursor.execute(sql).fetchall()
    conn.close()
    return res


def get_tables(db_dir, db_id) -> set[str]:
    db_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    res = exec_sql(db_file, "SELECT name FROM sqlite_master WHERE type='table'")
    return set(map(lambda r: r[0].lower(), res))


def cols(db_dir, db_id, t) -> List[ColDeclr]:
    db_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    res = exec_sql(db_file, f"PRAGMA table_info({t})")
    return list(map(lambda r: ColDeclr(t, r[1].lower(), r[2].lower(), r[5]), res))


def get_fks(db_dir, db_id, t) -> List[FKDeclr]:
    db_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    res = exec_sql(db_file, f"PRAGMA foreign_key_list({t})")
    return list(map(lambda r: FKDeclr(t, r[2].lower(), r[3].lower(), r[4].lower() if r[4] else None), res))


def save_meta(db_dir, db_id):
    m = Metadata()
    tables = get_tables(db_dir, db_id)
    fks = []
    pks = dict()
    for t in tables:
        m.add_table(t)
        columns = cols(db_dir, db_id, t)
        for col in columns:
            if col.pk:
                m.add_column(table_name=t, column_name=col.name, sdtype='id')
                m.set_primary_key(column_name=col.name, table_name=t)
                pks[t] = col.name
            else:
                sdt = get_sd_stype(col.type)
                m.add_column(table_name=t, column_name=col.name, sdtype=sdt)
        fks.extend(get_fks(db_dir, db_id, t))
    # m.update_column(table_name="appellations", column_name="appelation", sdtype="id")
    # m.add_alternate_keys(table_name="appellations", column_names=["appelation"])
    for fk in fks:
        try:
            m.update_column(table_name=fk.src_table, column_name=fk.src, sdtype="id")
            m.add_relationship(fk.dst_table, fk.src_table, fk.dst if fk.dst else pks[fk.dst_table], fk.src)
        except Exception as e:
            print(f"Failed to add rel[{db_id}]: {e}")
            raise e

    m.save_to_json(os.path.join(db_dir, db_id, "meta.json"), mode="overwrite")


skips = ["musical", "voter_1", "cre_Theme_park"]


def table_meta():
    errc = 0
    failed_dbs = set()
    for db_id in os.listdir("data/database"):
        print("Processing:", db_id)
        if not db_id.startswith("."):
            try:
                save_meta("data/database", db_id)
            except Exception as e:
                errc += 1
                print(f"{db_id}: Failed")
                print(e)
                failed_dbs.add(db_id)
    print("Failed:", failed_dbs)
    print(errc)
