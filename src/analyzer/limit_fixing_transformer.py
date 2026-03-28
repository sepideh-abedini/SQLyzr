import re

from src.analyzer.letter_casing_transformer import SqlTransformer
from src.analyzer.sql_data import SqlParsedData


class LimitRemoverTransformer(SqlTransformer):
    def msg(self) -> str:
        return "Limit clause in the predicted SQL query should be fixed."

    def delete_limit(self, sql: str) -> str:
        return re.sub(r'(.*)limit\s*([^\s]*)(.*)', r"\1\3", sql, flags=re.IGNORECASE)

    def transform_sql(self, pred: SqlParsedData, gold: SqlParsedData) -> (SqlParsedData, SqlParsedData):
        pred.sql = self.delete_limit(pred.sql)
        gold.sql = self.delete_limit(gold.sql)
        return pred, gold


class FixPredLimitTransformer(SqlTransformer):
    def msg(self) -> str:
        return "The limit value in the SQL query should change to"

    def replace_limit_expr(self, sql: str, gold_limit_expr) -> str:
        s = f"\\g<1>\\g<2>{gold_limit_expr}\\g<4>"
        return re.sub(r'(.*)(limit\s*)([^\s]*)(.*)', s, sql, flags=re.IGNORECASE)

    def transform_sql(self, pred: SqlParsedData, gold: SqlParsedData) -> (SqlParsedData, SqlParsedData):
        match = re.match(r'(.*)limit\s*([^\s]*)(.*)', gold.sql, flags=re.IGNORECASE)
        if match is not None:
            gold_limit_expr = match.groups()[1]
            pred.sql = self.replace_limit_expr(pred.sql, gold_limit_expr)
        return pred, gold
