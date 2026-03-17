import csv
import os
import shutil
import sqlite3
from pathlib import Path


def insert_rows_from_csv(cursor, table_name: str, csv_path: str):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)

        columns = ", ".join([f'"{col}"' for col in headers])
        placeholders = ", ".join(["?"] * len(headers))
        query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders})'

        for row in reader:
            try:
                cursor.execute(query, row)
            except sqlite3.IntegrityError as e:
                print(f"Failed to insert data: {row}, {e}")


def get_existing_table_name(cursor, table_base: str) -> str:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [row[0] for row in cursor.fetchall()]

    table_name = next(
        (t for t in existing_tables if t.lower() == table_base.lower()),
        None
    )

    if table_name is None:
        raise ValueError(f"Table '{table_base}' does not exist in database.")

    return table_name


def backup_and_revert(db_file: str):
    db_id = Path(db_file).name
    db_file_dir = Path(db_file).parent

    backup_path = os.path.join(db_file_dir, f"{db_id}.backup.sqlite")
    if os.path.exists(backup_path):
        os.remove(db_file)
        shutil.copyfile(backup_path, db_file)
        print("Database backup restored")
    else:
        shutil.copyfile(db_file, backup_path)
        print("Database backup created")


def total_rows(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cur.fetchall()]

    rows_per_table = []
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        num_rows = cur.fetchone()[0]
        rows_per_table.append(num_rows)

    return rows_per_table


def insert_synthetic_data(db_dir, db_id):
    db_parent = os.path.join(db_dir, db_id)
    db_file = os.path.join(db_parent, f"{db_id}.sqlite")

    backup_and_revert(db_file)

    before_rows = total_rows(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF;")

    csv_files = [f for f in os.listdir(db_parent) if f.endswith('.csv')]

    for name in csv_files:
        table_base = name.replace('_synthetic.csv', '')
        table_name = get_existing_table_name(cursor, table_base)
        csv_path = os.path.join(db_parent, name)
        insert_rows_from_csv(cursor, table_name, csv_path)
        print(f"Synthetic data inserted: {table_name}")

        # df = pd.read_csv(os.path.join(db_dir, name))
        # df.to_sql(table_name, conn, schema=None, method="multi", if_exists='append', index=False)

    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()

    after_rows = total_rows(db_file)

    print(f"Synthetic data inserted: {db_id}: {before_rows}({sum(before_rows)}) => {after_rows}({sum(after_rows)})")


def main():
    insert_synthetic_data("data/database_s10/driving_school")


if __name__ == '__main__':
    main()
