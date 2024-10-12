from src.batch.batch_feature_extractor import BatchFeatureExporter
from src.batch.batch_sql_parser import BatchSqlParser
from src.batch.numeric_feature_processor import NumericFeaturesProcessor
from config import CONFIG
from src.evaluator.din_preprocessor import DinResultPreProcessor
from src.evaluator.din_evaluator import DinResultEvaluator


def main():
    sql_processor = BatchSqlParser()
    stmts = sql_processor.process(CONFIG.sql_path())
    stmts = stmts[:10]
    feature_processor = BatchFeatureExporter(CONFIG.tables_path(), CONFIG.features_path())
    res = feature_processor.process(stmts)
    processor = NumericFeaturesProcessor('exprs/features.num.csv')
    processor.process(res)
    pred_file_path = 'out/pred.csv'
    pre_processor = DinResultPreProcessor("exprs/results.csv", pred_file_path)
    pre_processor.process()

    evaluator = DinResultEvaluator(pred_file_path, "exprs/eval.csv", "data/datasets/spider/database")
    df = evaluator.process()


if __name__ == '__main__':
    main()
