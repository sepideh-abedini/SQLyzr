import os.path
from src.scalar.utils.table_meta import get_tables, exec_sql


def get_db_stats(db_dir, db_id):
    db_file = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
    tables = get_tables(db_dir, db_id)

    for table in sorted(tables):
        try:
            result = exec_sql(db_file, f"SELECT COUNT(*) FROM {table}")
            row_count = result[0][0]
            print(f"{table:<30} {row_count:<10}")
        except Exception as e:
            print(f"{table:<30} Error: {str(e)}")
    print("-" * 40)
