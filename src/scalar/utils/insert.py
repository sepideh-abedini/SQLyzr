import os
import sqlite3

import pandas as pd
from loguru import logger

from src.scalar.utils.table_meta import get_tables


def get_correct_table_name(tables, table_name):
    for t in tables:
        if t.lower() == table_name.lower():
            return t
    raise RuntimeError(f"Table {table_name} not found in tables: {tables}")


def insert_synth_data(db_dir, db_id):
    conn = sqlite3.connect(os.path.join(db_dir, db_id, f"{db_id}.sqlite"))
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF;")

    tables = get_tables(db_dir, db_id)
    csv_files = [f for f in os.listdir(os.path.join(db_dir, db_id)) if f.endswith('.csv')]

    for name in csv_files:
        df = pd.read_csv(os.path.join(db_dir, db_id, name))
        table_name = get_correct_table_name(tables, name.replace('_synthetic.csv', ''))
        df.to_sql(table_name, conn, schema=None, method="multi", if_exists='append', index=False)
        logger.info(f"Inserted {name} into {db_id}")

    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()
