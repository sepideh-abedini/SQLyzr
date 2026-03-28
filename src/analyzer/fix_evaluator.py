from src.analyzer.fix_finder import FixRule, get_row_props, get_rs_props
from loguru import logger
from src.analyzer.letter_casing_transformer import SqlTransformer
from src.analyzer.list_matcher import match_list_of_list_full_prop
from src.analyzer.sql_data import SqlInputData, SqlParsedData
from src.db.sqlite_facade import SqliteFacade
from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser


def compare_with_fix(rs1, rs2, rules: frozenset[FixRule]):
    row_props = get_row_props(rules)
    rs_props = get_rs_props(rules)

    m = match_list_of_list_full_prop(rs1, rs2, rs_props, row_props)

    return m


class FixFinder:
    def __init__(self, ds_conf: DatasetConfig, trs: frozenset[SqlTransformer], rules: frozenset[FixRule]):
        self.rules = rules
        self.trs = trs
        self.parser = ExactMatchParser(ds_conf.get_tables_path())
        self.dbf = SqliteFacade(ds_conf)

    def parse(self, data: SqlInputData) -> SqlParsedData:
        ast = self.parser.parse(data.sql, data.db_id)
        return data.to_parsed(ast)

    def evaluate_strict(self, db_id: str, pred_sql: str, gold_sql: str):
        pred_res = self.dbf.exec_query_sync(db_id, pred_sql)
        gold_res = self.dbf.exec_query_sync(db_id, gold_sql)

        return pred_res == gold_res

    def evaluate(self, db_id: str, pred_sql: str, gold_sql: str):

        pred = SqlInputData(db_id, pred_sql)
        gold = SqlInputData(db_id, gold_sql)
        pred_parsed, gold_parsed = self.parse(pred), self.parse(gold)

        if pred_parsed is None or gold_parsed is None:
            return False

        for t in self.trs:
            pred_parsed, gold_parsed = t.transform_sql(pred_parsed, gold_parsed)

        pred_res = self.dbf.exec_query_sync(db_id, pred_parsed.sql)
        gold_res = self.dbf.exec_query_sync(db_id, gold_parsed.sql)

        m = compare_with_fix(pred_res, gold_res, self.rules)

        if m is not None and len(m) > 0:
            return True

        return False
