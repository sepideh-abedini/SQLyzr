import os
from dataclasses import dataclass, replace
from os import path
from typing import Literal, Optional


@dataclass(frozen=True)
class DatasetConfig:
    dataset_dir: str
    test_file: str
    train_file: str
    gold_file: str
    tables_file: str
    db_dir: str
    ver: Optional[str] = None
    mysql: bool = False
    dataset_type: Literal['spider', 'bird', 'beaver'] = 'spider'
    aug_db_id: Optional[str] = None

    @property
    def gold_file_ver(self) -> str:
        if self.ver is None:
            return self.gold_file
        else:
            return self.gold_file.replace(".txt", f".{self.ver}.txt")

    @property
    def test_file_ver(self) -> str:
        if self.ver is None:
            return self.test_file
        else:
            return self.test_file.replace(".json", f".{self.ver}.json")

    def get_rel_path(self, sub_path: str):
        return path.join(self.dataset_dir, sub_path)

    def get_test_path(self):
        return self.get_rel_path(self.test_file_ver)

    def get_gold_path(self):
        return self.get_rel_path(self.gold_file_ver)

    def get_train_path(self):
        return self.get_rel_path(self.train_file)

    def get_tables_path(self):
        return self.get_rel_path(self.tables_file)

    def get_db_path(self):
        return self.get_rel_path(self.db_dir)

    def get_db_description_path(self, db_id: str):
        desc_dir = os.path.join(self.db_dir, db_id, "database_description")
        return self.get_rel_path(desc_dir)

    def get_db_file_path(self, db_id: str, scale: int = 1):
        if scale == 1:
            db_file = os.path.join(self.db_dir, db_id, f"{db_id}.sqlite")
        else:
            db_file = os.path.join(f"{self.db_dir}_{scale}", db_id, f"{db_id}.sqlite")
        return self.get_rel_path(db_file)

    def __str__(self):
        return self.dataset_dir

    def to_ver(self, ver: str):
        return replace(self, ver=ver)
