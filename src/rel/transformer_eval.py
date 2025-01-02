import os.path

import pandas as pd

from src.eval.evaluator import get_pred_gold_db_id
from src.eval.metrics import RelaxedExecAcc, ExecAcc
from src.eval.model_eval_config import ModelEvalConfig
from src.rel.base_matcher import SubsetMatcher
from src.rel.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.rel.sql_data import SqlInputData
from src.rel.sql_transformer import LimitRemoverTransformer, LiteralCorrectorTransformer, ColCorrectorTransformer
from src.rel.transformer_detector import TransformerDetector


def find_transformers(config: ModelEvalConfig):
    ea = ExecAcc("ea", config.dataset_config)
    rea = RelaxedExecAcc("rea", config.dataset_config)
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
        for pred_str, gold_str, db_id in data:
            pred = SqlInputData(db_id, pred_str)
            gold = SqlInputData(db_id, gold_str)
            working_sub = detector.find_working_sub(pred, gold)
            results.append({
                "db_id": db_id,
                "pred": pred.sql,
                "gold": gold.sql,
                "transformers": working_sub,
                "ea": ea.calc(gold_str, pred_str, db_id),
                "rea": rea.calc(gold_str, pred_str, db_id)
            })
        df = pd.DataFrame(results)
        df.to_csv(os.path.join("data", "rel", f"transformers_{conf.temp}_{conf.itr}.csv"))
