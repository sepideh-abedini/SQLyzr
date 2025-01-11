import os.path
from typing import List, Set, Type

import pandas as pd
from tqdm.auto import tqdm

from src.eval.evaluator import get_pred_gold_db_id
from src.eval.metrics import RelaxedExecAcc, ExecAcc
from src.eval.model_eval_config import ModelEvalConfig
from src.rel.base_matcher import SubsetMatcher
from src.rel.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.rel.sql_data import SqlInputData
from src.rel.sql_processor import SqlMatchingProcessor
from src.rel.sql_transformer import LimitRemoverTransformer, LiteralCorrectorTransformer, ColCorrectorTransformer, \
    AddLimitTransformer
from src.rel.transformer_detector import TransformerDetector


def get_transformers_classes(working_sub: List[SqlMatchingProcessor]) -> Set[Type[SqlMatchingProcessor]]:
    return set(map(lambda p: p.__class__, working_sub))


def calc_rea_score(working_sub: List[SqlMatchingProcessor], config: ModelEvalConfig) -> int:
    if working_sub is None:
        return 0
    rea = RelaxedExecAcc("rea", config.dataset_config)
    rea_procs = get_transformers_classes(rea.detector.processors)
    working_procs = get_transformers_classes(working_sub)
    return 1 if working_procs.issubset(rea_procs) else 0


async def find_transformers(config: ModelEvalConfig):
    ea = ExecAcc("ea", config.dataset_config)
    detector = TransformerDetector(config.dataset_config, [
        LimitRemoverTransformer(),
        AddLimitTransformer(),
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
        for idx, (pred_str, gold_str, db_id) in tqdm(enumerate(data), leave=False, position=0, total=len(data)):
            if idx != 14:
                continue
            # if idx < 460:
            #     continue
            pred = SqlInputData(db_id, pred_str)
            gold = SqlInputData(db_id, gold_str)
            working_sub = await detector.find_working_sub_sync(pred, gold)
            rea_score = calc_rea_score(working_sub, config)
            ea_score = ea.calc(gold_str, pred_str, db_id)
            results.append({
                "db_id": db_id,
                "pred": pred.sql,
                "gold": gold.sql,
                "transformers": working_sub,
                "ea": ea_score,
                "rea": rea_score
            })
        df = pd.DataFrame(results)
        df.to_csv(os.path.join("data", "rel", f"transformers_{conf.temp}_{conf.itr}.csv"))
