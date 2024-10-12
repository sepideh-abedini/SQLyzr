from src.evaluator.str_visitor import StringVisitor
from src.prop_collectors.feature_extractor import SqlFeatureExtractor
from src.sql_parser.node import SelectStatementNode
from src.sql_parser.parser import SqlParser
from src.util.file_utils import load_csv
from src.util.str_utils import get_colored_diff
from tests.utils import clean_sql_str
import difflib


def diff(gold: SelectStatementNode, pred: SelectStatementNode):
    return gold


def proc_row(idx, row):
    parser = SqlParser()
    gold_str = row['gold']
    pred_str = row['pred']
    gold = "SELECT country,  count(*) FROM singer GROUP BY country"
    pred = "SELECT COUNT(Singer_ID) AS NumberOfSingers, Country FROM singer GROUP BY Country"

    visitor = StringVisitor()

    gold_stmt = parser.parse(gold_str)
    pred_stmt = parser.parse(pred_str)

    print("--------------------------")
    print(f"####ROW ID: {idx}#######")
    if gold_stmt is None or pred_stmt is None:
        print("Skipping ")
        print("---------------------------------------")
        return

    print("DB: ", row['db_id'])
    print("NLQ: ", row['nlq'])
    print("RAW: ")
    print(gold_str)
    print(pred_str)
    print(get_colored_diff(gold_str, pred_str))

    print("STMT: ")
    gold_stmt_str = gold_stmt.accept(visitor)
    pred_stmt_str = pred_stmt.accept(visitor)
    print(gold_stmt_str)
    print(pred_stmt_str)
    print(get_colored_diff(gold_stmt_str, pred_stmt_str))
    print("---------------------------------------")


df = load_csv('out/eval.csv')
df = df[df['eval'] == False]
for i, row in df.iterrows():
    proc_row(i, row)

# gold = "SELECT country,  count(*) FROM singer GROUP BY country"
# pred = "SELECT COUNT(Singer_ID) AS NumberOfSingers, Country FROM singer GROUP BY Country"
# parser = SqlParser()
# gold_stmt = parser.parse(gold)
# pred_stmt = parser.parse(pred)

# gold_stmt_str = clean_sql_str(str(gold_stmt))
# pred_stmt = parser.parse(pred)
# pred_stmt_str = clean_sql_str(str(pred_stmt))

# print(gold_stmt_str)
# print(pred_stmt_str)

# print(diff(gold_stmt, pred_stmt))
# stmt = parser.parse("SELECT name ,  country ,  age FROM singer ORDER BY age DESC")
# stmt.db_id = "concert_singer"
#
# props_extractor = PropsExtractor("data/datasets/spider/tables.json")
# props = props_extractor.extract_props(stmt)

# processor = DiffProcessor('tmp/exprs/eval.csv', 'tmp/exprs/diff.csv')
# processor.process()
