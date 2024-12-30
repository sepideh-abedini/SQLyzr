from typing import List

from pandas import DataFrame

from src.evaluator.dataframe_transformer import DataFrameTransformer


class DinResultPreProcessor(DataFrameTransformer):
    def get_columns(self) -> List[str]:
        return []

    def __init__(self, in_path, out_path):
        super().__init__(in_path, out_path)

    def process_df(self, df: DataFrame) -> DataFrame:
        df['id'] = df.index
        return df[['id', 'DATABASE', 'GOLD SQL', 'PREDICTED SQL', 'NLQ']].rename(
            columns={'NLQ': 'nlq', 'PREDICTED SQL': "pred", "GOLD SQL": "gold",
                     "DATABASE": "db_id"})
