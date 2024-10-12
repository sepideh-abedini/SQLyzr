from batch.transformer_evaluator import TransformerEvaluator
from evaluator.din_evaluator import DinResultEvaluator


def main():
    in_path = 'out/eval.csv'
    out_path = 'out/eval_transformed.csv'
    db_path = 'data/datasets/spider/database'


    evaluator = TransformerEvaluator(in_path=in_path, out_path=out_path, dbs=db_path)
    df = evaluator.process()

if __name__ == '__main__':
    main()
