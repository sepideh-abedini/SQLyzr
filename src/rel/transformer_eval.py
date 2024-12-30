import os.path

import pandas as pd

from src.eval.dataset_config import DatasetConfig
from src.eval.evaluator import get_pred_gold_db_id
from src.eval.model_eval_config import ModelEvalConfig
from src.rel.base_matcher import SubsetMatcher
from src.rel.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.rel.sql_data import SqlInputData
from src.rel.sql_transformer import LimitRemoverTransformer, LiteralCorrectorTransformer, ColCorrectorTransformer
from src.rel.transformer_detector import TransformerDetector


def eval_transformer(config: ModelEvalConfig):
    detector = TransformerDetector(config.dataset_config, [
        LimitRemoverTransformer(),
        LiteralCorrectorTransformer(),
        ColCorrectorTransformer(),
        IgnoreListOrderTransformer(),
        IgnoreColOrderTransformer(),
        SubsetMatcher()
    ])
    for conf in config.get_run_confs():
        pred_path = conf.get_pred_path()
        gold_path = conf.dataset_config.get_gold_path()
        data = get_pred_gold_db_id(pred_path, gold_path)
        results = []
        for gold, pred, db_id in data:
            pred = SqlInputData(db_id, pred)
            gold = SqlInputData(db_id, gold)
            working_sub = detector.find_working_sub(pred, gold)
            results.append({
                "db_id": db_id,
                "pred": pred.sql,
                "gold": gold.sql,
                "transformers": working_sub
            })
        df = pd.DataFrame(results)
        df.to_csv(os.path.join("data", "rel", f"transformers_{conf.temp}_{conf.itr}.csv"))
