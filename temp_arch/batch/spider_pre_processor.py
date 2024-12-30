from pandas import DataFrame

from src.util.file_utils import load_json


class SpiderPreProcessor:
    """Input: Json[{'db_id', 'query', 'questions'}]
       OUTPUT: CSV['id', 'db_id', 'sql', 'question']"""

    def __init__(self, in_path: str, out_path: str):
        self.in_path = in_path
        self.out_path = out_path

    def process(self):
        df = load_json(self.in_path)
        df = self.process_df(df)
        df.to_csv(self.out_path)

    def process_df(self, df: DataFrame) -> DataFrame:
        df['id'] = df.index
        df = df[['id', 'db_id', 'query', 'question']].rename(
            columns={'query': 'sql'})
        return df
