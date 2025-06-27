import os
import os.path

from src.scalar.utils.export_ddls import exec_sql, has_composite_pk


def generate_migration_script(db_dir, db_id):
    sqlite_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    res = exec_sql(sqlite_file, "SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in res]
    migration_lines = []

    for table in tables:
        columns = exec_sql(sqlite_file, f"PRAGMA table_info('{table}')")
        pk_columns = [col[1] for col in columns if col[5] > 0]

        fks = exec_sql(sqlite_file, f"PRAGMA foreign_key_list({table})")

        fk_columns = [fk[3] for fk in fks]
        pk_fk_columns = [col for col in pk_columns if col in fk_columns]

        if has_composite_pk(sqlite_file, table) or pk_fk_columns:
            new_pk = f"{table}_pk"

            fk_dict = {}
            for fk in fks:
                from_col = fk[3]
                to_table = fk[2]
                to_col = fk[4]
                fk_dict[from_col] = (to_table, to_col)

            col_defs = []
            for col in columns:
                name = col[1]
                col_type = col[2]
                not_null = "NOT NULL" if col[3] == 1 else ""
                default = f"DEFAULT {col[4]}" if col[4] is not None else ""

                if name in fk_dict:
                    to_table, to_col = fk_dict[name]
                    col_defs.append(f'{name} {col_type} {not_null} {default} REFERENCES {to_table}({to_col})'.strip())
                else:
                    if name in pk_columns:
                        col_defs.append(f'{name} {col_type} {not_null} {default}'.strip())
                    else:
                        col_defs.append(f'{name} {col_type} {not_null} {default}'.strip())

            col_defs.append(f'{new_pk} TEXT PRIMARY KEY')

            col_names = [f'{col[1]}' for col in columns]

            if pk_fk_columns and len(pk_columns) == 1:
                concat_expr = f'CAST({pk_columns[0]} AS TEXT)'
            else:
                concat_expr = " || '_' || ".join([f'CAST({col} AS TEXT)' for col in pk_columns])
            new_col_names = col_names + [f'{concat_expr} AS {new_pk}']

            migration_lines.append(f"-- Migration for table {table}")
            migration_lines.append(f"ALTER TABLE {table} RENAME TO {table}_old;")
            migration_lines.append(
                f"CREATE TABLE {table} (\n " + ',\n  '.join(col_defs) + "\n);"
            )

            migration_lines.append(
                f"INSERT INTO {table} ({', '.join(col_names)}, {new_pk})\n"
                f"SELECT {', '.join(new_col_names)} FROM {table}_old;"
            )
            migration_lines.append(f"DROP TABLE {table}_old;\n")
    if len(migration_lines) > 0:
        migration_path = os.path.join(db_dir, db_id, "migration.sql")
        with open(migration_path, "w") as f:
            f.write("\n".join(migration_lines))


def main():
    db_dir = "data/database"
    db_ids = os.listdir(db_dir)
    for db_id in db_ids:
        if not db_id.startswith("."):
            generate_migration_script(db_dir, db_id)


if __name__ == '__main__':
    main()
