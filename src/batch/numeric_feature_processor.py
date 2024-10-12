from dataclasses import dataclass

from pandas import DataFrame
from tqdm import tqdm

from src.util.file_utils import save_csv
from src.prop_collectors.sql_features import SqlFeatures


@dataclass
class NumericSqlFeatures:
    id: int
    max_join_tables: int
    unique_tables: int
    unique_funs: int
    unique_bin_ops: int
    unique_cols: int
    has_order_by: int
    has_limit: int
    has_group: int
    max_nest_level: int
    tree_size: int
    tree_height: int


class NumericFeaturesProcessor:
    def __init__(self, out_path: str):
        self.out_path = out_path

    def process(self, df: DataFrame):
        df = self.process_features(df)
        save_csv(df, self.out_path)

    def process_features(self, df: DataFrame) -> DataFrame:
        rows = []
        for _, row in tqdm(df.iterrows(), desc=self.__class__.__name__):
            rows.append(self.to_numeric_features(row))
        return DataFrame(rows)

    def to_numeric_features(self, features: SqlFeatures) -> NumericSqlFeatures:
        return NumericSqlFeatures(
            id=features.id,
            max_join_tables=max(features.join_tables_count_list + [0]),
            unique_tables=len(features.table_set),
            unique_funs=len(features.fun_set),
            unique_bin_ops=len(features.bin_op_set),
            unique_cols=len(features.col_set),
            has_group=int(features.has_group),
            has_order_by=int(features.has_order_by),
            has_limit=int(features.has_limit),
            max_nest_level=features.max_nest_level,
            tree_size=features.max_tree_size,
            tree_height=features.max_tree_height
        )
