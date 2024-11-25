import os
from dataclasses import dataclass
from os import path
from dataclasses import replace


@dataclass
class DatasetConfig:
    dataset_dir: str
    data_file: str
    gold_file: str
    tables_file: str
    db_dir: str

    def get_rel_path(self, sub_path: str):
        return path.join(self.dataset_dir, sub_path)

    def get_data_path(self):
        return self.get_rel_path(self.data_file)

    def get_gold_path(self):
        return self.get_rel_path(self.gold_file)

    def get_tables_path(self):
        return self.get_rel_path(self.tables_file)

    def get_db_path(self):
        return self.get_rel_path(self.db_dir)

    def get_db_file_path(self, db_id: str):
        db_file = os.path.join(self.db_dir, db_id, f"{db_id}.sqlite")
        return self.get_rel_path(db_file)


SPIDER_SMALL = DatasetConfig(
    dataset_dir="data/spider",
    data_file="dev.small.json",
    gold_file="dev.small.gold.txt",
    tables_file="tables.json",
    db_dir="database"
)
