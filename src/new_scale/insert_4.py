import os

from src.new_scale.insert import insert_synthetic_data


def insert_dbs(dbs_dir):
    errc = 0
    total = 0
    done = 0
    for db_id in os.listdir(dbs_dir):
        if not db_id.startswith("."):
            total += 1
            try:
                db_dir = os.path.join(dbs_dir, db_id)
                insert_synthetic_data(db_dir)
                print(f"Insertion done: {db_id}")
                done += 1
            except Exception as e:
                print(e)
                print(f"Insertion failed: {db_id}")
                errc += 1
    print(errc, done, total)
    print("Inserting data done")


def main():
    insert_dbs("data/database_s1000")

