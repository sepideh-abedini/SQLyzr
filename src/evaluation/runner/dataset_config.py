from dataclasses import dataclass
from os import path
from dataclasses import replace


@dataclass
class DatasetConfig:
    dataset_dir: str
    data_file: str
    tables_file: str
    db_dir: str

    def get_rel_path(self, sub_path: str):
        return path.join(self.dataset_dir, sub_path)

    def get_data_path(self):
        return self.get_rel_path(self.data_file)

    def get_tables_path(self):
        return self.get_rel_path(self.tables_file)

    def get_db_path(self):
        return self.get_rel_path(self.db_dir)


SPIDER_SMALL = DatasetConfig(
    dataset_dir="data/spider",
    data_file="dev.small.json",
    tables_file="tables.json",
    db_dir="database"
)
