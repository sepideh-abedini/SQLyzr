import sqlite3
import csv
import os
import shutil
from typing import List

from src.scalar.utils.table_meta import FKDeclr


def exec_sql(file, sql):
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    res = cursor.execute(sql).fetchall()
    conn.close()
    return res


def apply_migration(db_dir, db_id):
    sqlite_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    backup_file = sqlite_file + '.bak'
    mig_file = os.path.join(db_dir, db_id, "migration.sql")
    if not os.path.exists(backup_file):
        shutil.copy(sqlite_file, backup_file)
    if os.path.exists(backup_file):
        revert_backup(db_dir, db_id)
    if not os.path.exists(mig_file):
        return
    conn = sqlite3.connect(sqlite_file)
    try:
        with open(mig_file, 'r') as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()
    finally:
        conn.close()


def get_fks(db_dir, db_id, t) -> List[FKDeclr]:
    db_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    res = exec_sql(db_file, f"PRAGMA foreign_key_list({t})")
    return list(map(lambda r: FKDeclr(t, r[2], r[3], r[4]), res))


def export_migration_script(db_dir, db_id):
    db_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    res = exec_sql(db_file, "SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in res]
    migration_lines = []

    for table in tables:
        fks = get_fks(db_dir, db_id, table)
        columns = exec_sql(db_file, f"PRAGMA table_info('{table}')")
        pk_columns = [col[1] for col in columns if col[5] > 0]

        new_pk = f"{table}_pk"
        if len(pk_columns) > 1:
            col_defs = []
            for col in columns:
                name = col[1]
                col_type = col[2]
                if name in pk_columns:
                    col_defs.append(f'{name} {col_type}')
                else:
                    col_defs.append(f'{name} {col_type}')
            col_defs.append(f'{new_pk} TEXT PRIMARY KEY')

            col_names = [f'{col[1]}' for col in columns]
            concat_expr = " || '-' || ".join([f'CAST({col} AS TEXT)' for col in pk_columns])
            new_col_names = col_names + [f'{concat_expr} AS {new_pk}']

            migration_lines.append(f"-- Migration for table {table}")
            migration_lines.append(f"ALTER TABLE {table} RENAME TO {table}_old;")
            migration_lines.append(
                f"CREATE TABLE {table} (\n  {', '.join(col_defs)}\n);"
            )
            migration_lines.append(
                f"INSERT INTO {table} ({', '.join(col_names)}, {new_pk})\n"
                f"SELECT {', '.join(new_col_names)} FROM {table}_old;"
            )
            migration_lines.append(f"DROP TABLE {table}_old;\n")

    migration_path = os.path.join(db_dir, db_id, "migration.sql")
    with open(migration_path, "w") as f:
        f.write("\n".join(migration_lines))


def has_composite_pk(file, table):
    res = exec_sql(file, f"PRAGMA table_info({table})")
    pk_rows = list(filter(lambda r: r[5] > 0, res))
    return len(pk_rows) > 1


def revert_backup(db_dir, db_id):
    db_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    if os.path.exists(db_file + '.bak'):
        shutil.copy(db_file + ".bak", db_file)


def export_ddl(db_dir, db_id):
    # revert_backup(db_dir, db_id)
    db_file = f'{db_dir}/{db_id}/{db_id}.sqlite'
    data = exec_sql(db_file, "SELECT name, sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")

    fks = []
    composite_tables = set()
    ddls = []
    for name, ddl in data:
        ddls.append(f"-- Table: {name}\n{ddl};\n")
        fks.extend(exec_sql(db_file, f"PRAGMA foreign_key_list({name});"))
        if has_composite_pk(db_file, name):
            composite_tables.add(name)
            # print(f"Table: {sqlite_file}-{name} has a composite pk")
    if len(composite_tables) > 0:
        print(db_id)
        print(len(composite_tables))
        export_migration_script(db_dir, db_id)
        apply_migration(db_file, os.path.join(db_dir, db_id, "migration.sql"))

    referenced_composed_tables = set()
    for fk in fks:
        referenced_table = fk[2]
        if referenced_table in composite_tables:
            referenced_composed_tables.add(referenced_table)
    if len(referenced_composed_tables) > 0:
        print(db_id)
        print(referenced_composed_tables)

    ddl_text = "\n".join(ddls)

    output_file = f'{db_dir}/{db_id}/ddl.sql'
    if output_file:
        with open(output_file, 'w') as f:
            f.write(ddl_text)
    else:
        print(ddl_text)


def export_all_ddls():
    path = "data/database"
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    for db_id in dirs:
        export_ddl(path, db_id)
    # db_id = "department_management"
    # export_ddl(f'data/database/{db_id}/{db_id}.sqlite', f'data/database/{db_id}/ddl.sql')


def export_csvs(db_dir, db_id):
    db_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    out_dir = os.path.join(db_dir, db_id, "ex")
    os.makedirs(out_dir, exist_ok=True)
    for (table_name,) in tables:
        rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        col_names = [description[0] for description in cursor.description]
        with open(os.path.join(out_dir, f"{table_name}.csv"), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(col_names)
            writer.writerows(rows)
    conn.close()


def main():
    export_all_ddls()
    # export_db_schema("data/database", "hospital_1")
    # export_csvs("data/database", "hospital_1")


if __name__ == '__main__':
    main()
