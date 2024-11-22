import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModelEvalConfig:
    dataset_path: str
    pred_dir: str
    eval_dir: str
    tables_file: str
    query_file: str  # json file containing the nl query
    gold_file: str  # a file containing gold sql corresponding to the query file
    database_dir: str
    scores_file: str

    def get_sub_path(self, path: str):
        return os.path.join(self.dataset_path, path)

    def get_query_file_path(self):
        return self.get_sub_path(self.query_file)

    def get_tables_file_path(self):
        return self.get_sub_path(self.tables_file)

    def get_gold_file_path(self):
        return self.get_sub_path(self.gold_file)

    def get_database_path(self):
        return self.get_sub_path(self.database_dir)

    def get_parent_dir(self):
        return Path(self.dataset_path).parent

    def get_dataset_dir(self):
        return os.path.basename(self.dataset_path)

    def get_chunk_path(self, i: int):
        return os.path.join(self.get_parent_dir(), f"{self.get_dataset_dir()}_{i}")

    def get_pred_path(self, temp: float, itr: int):
        return os.path.join(self.pred_dir, f"{temp}_{itr}.out")

    def get_eval_data_path(self, temp: float, itr: int):
        return os.path.join(self.eval_dir, f"{temp}_{itr}.csv")

    def get_gold_path_per_cat(self, temp: float, itr: int, cat: str):
        return os.path.join(self.eval_dir, f"{temp}_{itr}_{cat}.gold")

    def get_pred_path_per_cat(self, temp: float, itr: int, cat: str):
        return os.path.join(self.eval_dir, f"{temp}_{itr}_{cat}.pred")

    def get_scores_path(self, sub: str = ""):
        return os.path.join(self.eval_dir, f"scores_{sub}.csv")

    def get_database_file_path(self, db_id: str):
        return os.path.join(self.dataset_path, self.database_dir, db_id, f"{db_id}.sqlite")
