from src.evaluator.din_evaluator import DinResultEvaluator
from src.evaluator.din_preprocessor import DinResultPreProcessor


def main():
    pred_path = "out/pred.csv"
    pre_processor = DinResultPreProcessor("data/models/din/results.csv", pred_path)
    pre_processor.process()

    evaluator = DinResultEvaluator(pred_path, "out/eval.csv", "data/datasets/spider/database")
    df = evaluator.process()


if __name__ == '__main__':
    main()

# t = (1, 'salam')
# tf = ReverseTransformer()
#
# dbs_dir = "data/datasets/spider/database"
# db_facade = DatabaseFacade(dbs_dir)
# parser = SqlParser()

# evaluator = PredEvaluator(dbs_dir)
# evaluator = TransformerEvaluator(dbs_dir)
#
# df = load_csv('out/eval.csv')
# df = df[df['eval'] == False]
# # df = df[:10]
#
# s = 0
# for i, row in df.iterrows():
#     db_id = row['db_id']
#     gold_sql = row['gold']
#     pred_sql = row['pred']
#     res_equal = evaluator.eval(db_id, gold_sql, pred_sql)
#     if not res_equal:
#         gold_stmt = parser.parse(row['gold'])
#         pred_stmt = parser.parse(row['pred'])
#         gold_res, pred_res = evaluator.get_results(db_id, gold_sql, pred_sql)
#         print(f"NLQ:", row['nlq'])
#         print("SQLs: ")
#         print("Gold Sql: ", gold_sql)
#         print("Pred Sql: ", pred_sql)
#         print("Res: ")
#         print("Gold Res: ", gold_res)
#         print("Pred Res: ", pred_res)
#         print("SQL Diff:")
#         print(get_colored_diff(gold_sql, pred_sql))
#     else:
#         s += 1
#     print("-------------------------------------------")
#
# print(f"Num Mismatch: {len(df)}")
# print(f"Num Fixed With Tranformation: {s}")
