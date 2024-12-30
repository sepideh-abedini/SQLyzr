from typing import List

from pandas import DataFrame

from batch.csv_file_processor import CsvFileProcessor

NUM_OF_SAMPLES= 30


class SpiderSampler(CsvFileProcessor):

    """ Input: CSV['id', 'sql', 'cat','db_id', 'question']
        Output: CSV['id', 'sql', 'cat','db_id', 'question'] with the exact number of samples  """

    def __init__(self, in_path: str, out_path: str):
        super().__init__(in_path)
        self.out_path = out_path

    def get_columns(self) -> List[str]:
        return ['id', 'sql', 'cat','question','db_id']

    def process_df(self, df: DataFrame) -> DataFrame:
        df = df.groupby('cat').apply(lambda x: x.head(NUM_OF_SAMPLES)).reset_index(drop=True)
        df = df.rename({'sql': 'query'}, axis=1)
        df = df[['query', 'question', 'db_id']]
        return df

    def process(self):
        df = super().process()
        df.to_json(self.out_path, orient='records')



