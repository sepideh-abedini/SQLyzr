import os
from dataclasses import dataclass
from typing import Final


@dataclass
class SqlAnalyzerConfig:
    dataset_dir: str = ''
    dev_file: str = ''
    tables_file: str = ''
    out_dir: str = ''
    sql_file: str = ''
    features_file: str = ''
    graphs_file: str = ''
    graphs_dir: str = ''
    graphs_file_tpl: str = ''
    cats_file: str = ''
    tags_file: str = ''

    def __post_init__(self):
        os.makedirs(self.out_dir, exist_ok=True)
        os.makedirs(self.graphs_dir, exist_ok=True)

    def dev_path(self):
        return os.path.join(self.dataset_dir, self.dev_file)

    def tables_path(self):
        return os.path.join(self.dataset_dir, self.tables_file)

    def out_path(self, file_name: str):
        return os.path.join(self.out_dir, file_name)

    def sql_path(self):
        return self.out_path(self.sql_file)

    def features_path(self):
        return self.out_path(self.features_file)

    def graph_path_tpl(self):
        return os.path.join(self.graphs_dir, self.graphs_file_tpl)

    def cats_path(self):
        return self.out_path(self.cats_file)

    def graphs_path(self):
        return self.out_path(self.graphs_file)

    def tags_path(self):
        return self.out_path(self.tags_file)


CONFIG = SqlAnalyzerConfig(
    dataset_dir="data/datasets/spider",
    dev_file="dev.json",
    tables_file="tables.json",
    out_dir="out",
    sql_file="dev.sql.csv",
    features_file="features.csv",
    graphs_file="graphs.csv",
    graphs_dir="out/graphs",
    graphs_file_tpl="{}_spider",
    cats_file="cats.csv",
    tags_file="tags.csv"
)
