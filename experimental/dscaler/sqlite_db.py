import shutil
from pathlib import Path


class SqliteDatabase:
    db_dir: str

    def __init__(self, db_dir):
        self.db_dir = db_dir

    @property
    def db_ids(self):
        path = Path(self.db_dir)
        dirs = [p.name for p in path.iterdir() if p.is_dir()]
        return dirs

    def get_db_path(self, db_id):
        return Path(self.db_dir) / db_id / f"{db_id}.sqlite"

    def copy(self, dir_suffix):
        src_path = Path(self.db_dir)
        dst_path = self.db_dir + dir_suffix
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        return SqliteDatabase(dst_path)
