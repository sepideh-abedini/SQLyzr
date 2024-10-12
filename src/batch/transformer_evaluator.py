from typing import List, Tuple

from pandas import DataFrame

from evaluator.dataframe_transformer import DataFrameTransformer
from evaluator.db_facade import DatabaseFacade


def sort_transformer(tuples: List[Tuple])-> List[Tuple]:
    return sorted(tuples)



class TransformerEvaluator(DataFrameTransformer):
    def __init__(self, in_path: str, out_path: str, dbs: str):
        super().__init__(in_path, out_path)
        self.db_facade = DatabaseFacade(dbs)

    def get_columns(self) -> List[str]:
        return []

    def process_df(self, df: DataFrame) -> DataFrame:
        print(f"Before: {df[df['eval'] == False].count()}")
        for index, row in df.iterrows():
            if row['eval'] == False:
                gold = row['gold']
                pred = row['pred']
                db_id = row['db_id']
                gold_res = self.db_facade.execute_query(db_id, gold)
                pred_res = self.db_facade.execute_query(db_id, pred)
                trans_pred_res = sort_transformer(pred_res)
                df.loc[index, 'eval'] = (gold_res == trans_pred_res)
        print(f"Before: {df[df['eval'] == False].count()}")
        return df