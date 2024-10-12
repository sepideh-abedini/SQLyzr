from typing import TypedDict, cast, List

from pandas import DataFrame
from tqdm import tqdm

from src.evaluator.dataframe_transformer import DataFrameTransformer
from src.cat.categorizer import Categorizer
from src.cat.tag_extractor import TagExtractor
from src.evaluator.db_facade import DatabaseFacade
from src.sql_parser.parser import SqlParser

DB_PATH_PREFIX = "data/datasets/spider/database"
db_name = "concert_singer"


class PredRow(TypedDict):
    db_id: str
    pred: str
    gold: str


class DinResultEvaluator(DataFrameTransformer):
    db_facade: DatabaseFacade

    def __init__(self, in_path: str, out_path: str, dbs_dir: str):
        super().__init__(in_path, out_path)
        self.db_facade = DatabaseFacade(dbs_dir)
        self.sql_parser = SqlParser()
        self.tag_extractor = TagExtractor()
        self.categorizer = Categorizer()

    def evaluate_row(self, row: PredRow):
        db_id = row['db_id']
        gold_res = self.db_facade.execute_query(db_id, row['gold'])
        pred_res = self.db_facade.execute_query(db_id, row['pred'])
        row['eval'] = (gold_res == pred_res)
        row['cat'] = self.get_cat(row['gold'])
        return row

    def get_cat(self, sql: str):
        ast = self.sql_parser.parse(sql)
        tags = self.tag_extractor.extract_tags(ast)
        cat = self.categorizer.get_category(tags.tag_set)
        return cat

    def process_df(self, df: DataFrame) -> DataFrame:
        rows = []
        for _, row in tqdm(df.iterrows(), desc=self.__class__.__name__):
            rows.append(self.evaluate_row(cast(PredRow, row)))
        return DataFrame(rows)

    def get_columns(self) -> List[str]:
        return ['db_id', 'gold', 'pred']
