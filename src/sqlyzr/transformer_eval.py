import os.path
from typing import List, Set, Type

import pandas as pd
from tqdm.auto import tqdm

from src.configs.sqlyzr import SQLyzrConfig
from src.eval.metrics import RelaxedExecAcc, ExecAcc, GoldNotEmpty
from src.eval.model_eval_config import ModelEvalConfig
from src.rel.base_matcher import SubsetMatcher
from src.rel.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.rel.sql_data import SqlInputData
from src.rel.sql_processor import SqlMatchingProcessor
from src.rel.sql_transformer import LiteralCorrectorTransformer, ColCorrectorTransformer, \
    AddLimitTransformer
from src.rel.transformer_detector import TransformerDetector
from src.sqlyzr.evaluator import get_pred_gold_db_id
from src.sqlyzr.sqlyzr_processor import SqlyzrProcessor


class TransformerFinder(SqlyzrProcessor):
    async def run(self):
        await find_transformers(self.conf)


def get_transformers_classes(working_sub: List[SqlMatchingProcessor]) -> Set[Type[SqlMatchingProcessor]]:
    return set(map(lambda p: p.__class__, working_sub))


def calc_rea_score(working_sub: List[SqlMatchingProcessor], config: ModelEvalConfig) -> int:
    if working_sub is None:
        return 0
    rea = RelaxedExecAcc("rea", config.dataset_config)
    rea_procs = get_transformers_classes(rea.detector.processors)
    working_procs = get_transformers_classes(working_sub)
    return 1 if working_procs.issubset(rea_procs) else 0


async def find_transformers(config: SQLyzrConfig):
    ea = ExecAcc("ea", config.eval_conf.dataset_config)
    gne = GoldNotEmpty("gne", config.eval_conf.dataset_config)
    detector = TransformerDetector(config.eval_conf.dataset_config, [
        AddLimitTransformer(),
        LiteralCorrectorTransformer(),
        ColCorrectorTransformer(),
        IgnoreListOrderTransformer(),
        IgnoreColOrderTransformer(),
        SubsetMatcher()
    ])
    run_confs = config.eval_conf.get_run_confs()
    for conf in tqdm(run_confs, desc="Finding transformers", total=len(run_confs), leave=False, position=0):
        pred_path = conf.get_pred_path()
        gold_path = conf.dataset_config.get_gold_path()
        data = get_pred_gold_db_id(pred_path, gold_path)
        results = []
        for idx, (pred_str, gold_str, db_id) in tqdm(enumerate(data), desc=f"Finding transformer for {conf}",
                                                     leave=False, position=1, total=len(data)):
            pred = SqlInputData(db_id, pred_str)
            gold = SqlInputData(db_id, gold_str)
            working_sub = await detector.find_working_sub_sync(pred, gold)
            rea_score = calc_rea_score(working_sub, config.eval_conf)
            ea_score = await ea.calc(gold_str, pred_str, db_id)
            gold_is_empty = 1 - await gne.calc(gold_str, pred_str, db_id)
            results.append({
                "db_id": db_id,
                "pred": pred.sql,
                "gold": gold.sql,
                "transformers": working_sub,
                "ea": ea_score,
                "rea": rea_score,
                "GOLD_IS_EMPTY": gold_is_empty
            })
        df = pd.DataFrame(results)
        df.to_csv(conf.get_trs_path())


def post_process_transformers(config: SQLyzrConfig):
    print("salam")
    dfs = []
    for conf in config.eval_conf.get_run_confs():
        df = pd.read_csv(conf.get_trs_path(), index_col=0)
        df['tmp'] = conf.temp
        df['itr'] = conf.itr
        dfs.append(df)
    final = pd.concat(dfs, axis=0, ignore_index=True)
    final = final[(final['ea'] == 0) & (final['rea'] == 1)]
    final.to_csv(config.eval_conf.get_trs_result_path())
