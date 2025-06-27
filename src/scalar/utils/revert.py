import os

from export_ddls import revert_backup


def main():
    db_dir = "data/database"
    for db_id in os.listdir(db_dir):
        if not db_id.startswith("."):
            revert_backup(db_dir, db_id)


if __name__ == '__main__':
    main()
