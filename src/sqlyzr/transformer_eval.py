from typing import List, Set, Type

import pandas as pd
from tqdm.auto import tqdm

from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.metrics import RelaxedExecAcc, ExecAcc, GoldNotEmpty
from src.rel.base_matcher import ExtraColumnsMatcher, ExtraTupleMatcher, ExtraColumnAndTupleMatcher
from src.rel.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.rel.sql_data import SqlInputData
from src.rel.sql_processor import SqlMatchingProcessor
from src.rel.sql_transformer import LetterCasingTransformer, FixPredLimitTransformer
from src.rel.transformer_detector import TransformerDetector
from src.sqlyzr.pred_gold_reader import PredGoldReader


class TransformerFinder:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    @staticmethod
    def __get_transformers_classes(working_sub: List[SqlMatchingProcessor]) -> Set[Type[SqlMatchingProcessor]]:
        return set(map(lambda p: p.__class__, working_sub))

    def __calc_rea_score(self, working_sub: List[SqlMatchingProcessor]) -> int:
        if working_sub is None:
            return 0
        rea = RelaxedExecAcc("rea", self.__config.eval_conf.dataset_config)
        rea_procs = self.__get_transformers_classes(rea.detector.processors)
        working_procs = self.__get_transformers_classes(working_sub)
        return 1 if working_procs.issubset(rea_procs) else 0

    async def run(self):
        config = self.__config.eval_conf.dataset_config
        ea = ExecAcc("ea", config)
        gne = GoldNotEmpty("gne", config)
        detector = TransformerDetector(config, [
            FixPredLimitTransformer(),
            LetterCasingTransformer(),
            IgnoreListOrderTransformer(),
            IgnoreColOrderTransformer(),
            ExtraColumnsMatcher(),
            ExtraTupleMatcher(),
            ExtraColumnAndTupleMatcher()
        ])
        run_confs = self.__config.eval_conf.get_run_confs()
        for conf in tqdm(run_confs, desc="Finding transformers", total=len(run_confs), leave=False, position=0):
            reader = PredGoldReader(conf)
            data = reader.get_pred_gold_db_id()
            results = []
            for idx, (pred_str, gold_str, db_id) in tqdm(enumerate(data), desc=f"Finding transformer for {conf}",
                                                         leave=False, position=1, total=len(data)):
                pred = SqlInputData(db_id, pred_str)
                gold = SqlInputData(db_id, gold_str)
                working_sub = await detector.find_working_sub_sync(pred, gold)
                ea_score = await ea.calc(gold_str, pred_str, db_id)
                if ea_score > 0:
                    rea_score = 1
                else:
                    rea_score = self.__calc_rea_score(working_sub)
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

    def post_process(self):
        dfs = []
        for conf in self.__config.eval_conf.get_run_confs():
            df = pd.read_csv(conf.get_trs_path(), index_col=0)
            df['tmp'] = conf.temp
            df['itr'] = conf.itr
            dfs.append(df)
        final = pd.concat(dfs, axis=0, ignore_index=True)
        final = final[(final['ea'] == 0) & (final['rea'] == 1)]
        final.to_csv(self.__config.eval_conf.get_trs_result_path())
