from typing import Dict, Tuple, List

from src.evaluator.db_facade import DatabaseFacade
from src.evaluator.str_visitor import StringVisitor
from src.evaluator.tuple_transformer import PredEvaluator
from src.sql_parser.parser import SqlParser
from src.util.file_utils import load_csv, save_csv
from src.util.str_utils import get_colored_diff


def check_results(gold: List[Tuple], pred: List[Tuple]):
    if pred is None:
        return False
    if len(gold) != len(pred):
        return False
    gold = sorted(gold)
    if pred:
        pred = sorted(pred)
    for i in range(len(gold)):
        if len(gold[i]) > len(pred[i]):
            return False
        for j in range(len(gold[i])):
            if gold[i][j] != pred[i][j]:
                return False
    return True


def diff_row(row: Dict):
    dbs_dir = "data/datasets/spider/database"
    db_facade = DatabaseFacade(dbs_dir)
    parser = SqlParser()
    evaluator = PredEvaluator(dbs_dir)
    str_visitor = StringVisitor()
    db_id = row['db_id']
    gold_sql = row['gold']
    pred_sql = row['pred']
    gold_stmt = parser.parse(row['gold'])
    gold_stmt_str = gold_stmt.accept(str_visitor)

    pred_stmt = parser.parse(row['pred'])
    pred_stmt_str = ''
    if pred_stmt:
        pred_stmt_str = pred_stmt.accept(str_visitor)

    gold_res, pred_res = evaluator.get_results(db_id, gold_sql, pred_sql)
    gold_stmt_res, pred_stmt_res = evaluator.get_results(db_id, gold_stmt_str, pred_stmt_str)

    # return True

    print(f"NLQ:", row['nlq'])
    print("SQLs:")
    print("Pred:", pred_sql)
    print("Gold:", gold_sql)
    print("Diff:", get_colored_diff(gold_sql, pred_sql))
    print("Stmt SQLs:")
    print("Pred:", pred_stmt_str)
    print("Gold:", gold_stmt_str)
    print("Diff:", get_colored_diff(gold_stmt_str, pred_stmt_str))
    print("Res:")
    print("Pred:", pred_res)
    print("Gold:", gold_res)
    print("Stmt Res:")
    print("Pred:", pred_stmt_res)
    print("Gold:", gold_stmt_res)
    if check_results(gold_stmt_res, pred_stmt_res):
        print("FIXABLE")
    print("-------------------------------------------")
    return False


def main():
    df = load_csv("out/eval.csv")
    df = df[df['eval'] == False]
    save_csv(df, 'out/eval.false.csv')
    s = 0
    df = df.tail(180)
    for i, row in df.iterrows():
        if diff_row(row):
            s += 1
        text = input("Next?")
    print(f"Total: {len(df)}")
    print(f"Fixed: {s}")


nodes = []
data = {}

bar = [e for e in [data[node] for node in nodes]]

if __name__ == '__main__':
    main()

# evaluator = TransformerEvaluator(dbs_dir)
#
# df = load_csv('out/eval.csv')
# df = df[df['eval'] == False]
# # df = df[:10]
#
# s = 0
# for i, row in df.iterrows():
#
# print(f"Num Mismatch: {len(df)}")
# print(f"Num Fixed With Tranformation: {s}")
