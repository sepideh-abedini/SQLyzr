import os

from export_ddls import apply_migration


def main():
    db_dir = "data/database"
    for db_id in os.listdir(db_dir):
        if not db_id.startswith("."):
            try:
                db_file = f"{db_dir}/{db_id}/{db_id}.sqlite"
                apply_migration(db_dir, db_id)
            except Exception as e:
                print(f"Mig failed: {db_id}")
                print(e)


if __name__ == '__main__':
    main()
