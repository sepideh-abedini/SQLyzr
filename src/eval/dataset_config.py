import os
from dataclasses import dataclass, replace
from os import path
from typing import Literal


@dataclass(frozen=True)
class DatasetConfig:
    dataset_dir: str
    test_file: str
    train_file: str
    gold_file: str
    tables_file: str
    db_dir: str
    mysql: bool = False
    dataset_type: Literal['spider', 'bird'] = 'spider'

    def get_rel_path(self, sub_path: str):
        return path.join(self.dataset_dir, sub_path)

    def get_test_path(self):
        return self.get_rel_path(self.test_file)

    def get_train_path(self):
        return self.get_rel_path(self.train_file)

    def get_gold_path(self):
        return self.get_rel_path(self.gold_file)

    def get_tables_path(self):
        return self.get_rel_path(self.tables_file)

    def get_db_path(self):
        return self.get_rel_path(self.db_dir)

    def get_db_description_path(self, db_id: str):
        desc_dir = os.path.join(self.db_dir, db_id, "database_description")
        return self.get_rel_path(desc_dir)

    def get_db_file_path(self, db_id: str):
        db_file = os.path.join(self.db_dir, db_id, f"{db_id}.sqlite")
        return self.get_rel_path(db_file)

    def to_thread_conf(self, chunk_num: int):
        return replace(self, dataset_dir=f"{self.dataset_dir}_chunk_{chunk_num}")
