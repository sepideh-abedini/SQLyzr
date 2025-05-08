import os
from collections import defaultdict
from typing import List, Set, Type

import pandas as pd
from loguru import logger
from tqdm.auto import tqdm

from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.dataset_config import DatasetConfig
from src.eval.metrics import RelaxedExecAcc, ExecAcc, GoldNotEmpty
from src.eval.single_run_config import SingleRunConfig
from src.rel.result_matcher import ExtraColumnsMatcher, ExtraTupleMatcher, IgnoreListOrderMatcher, \
    IgnoreColOrderMatcher, MissingColumnsMatcher
from src.rel.sql_data import SqlInputData
from src.rel.sql_processor import SqlMatchingProcessor
from src.rel.sql_transformer import LetterCasingTransformer, FixPredLimitTransformer
from src.rel.transformer_detector import TransformerDetector
from src.sqlyzr.pred_gold_reader import PredGoldReader
from src.util.file_utils import write_json, file_exists_not_forced
from src.util.log_util import alog, log
from src.util.multi_thread_utils import exec_multi_process


def merge_trs_files(config: SQLyzrConfig):
    logger.info("Merging pred files")

    per_model_confs = defaultdict(list)
    for run_conf in config.eval_conf.get_run_confs():
        per_model_confs[run_conf.model].append(run_conf)

    for model, run_confs in per_model_confs.items():
        per_dataset_confs = defaultdict(list)
        for run_conf in run_confs:
            per_dataset_confs[run_conf.dataset_config.dataset_type].append(run_conf)

        dataset_types = list(per_dataset_confs.keys())
        logger.info(f"Merging files for model {model} across dataset types: {dataset_types}")

        model_base_dir = os.path.join(config.eval_conf.trs_dir, model)

        all_files = {}
        for dataset_type in dataset_types:
            dataset_dir = os.path.join(model_base_dir, dataset_type)
            if os.path.exists(dataset_dir):
                all_files[dataset_type] = []
                for f in os.listdir(dataset_dir):
                    p = os.path.join(dataset_dir, f)
                    if os.path.isfile(p) and p.endswith('.json'):
                        all_files[dataset_type].append(f)

        file_groups = defaultdict(list)
        for dataset_type, files in all_files.items():
            for file in files:
                file_groups[file].append((dataset_type, os.path.join(model_base_dir, dataset_type, file)))

        merged_dir = model_base_dir

        for file_name, file_paths in file_groups.items():
            if len(file_paths) == len(dataset_types):
                merged_file_path = os.path.join(merged_dir, file_name)
                logger.info(f"Merging {len(file_paths)} files into {merged_file_path}")

                with open(merged_file_path, 'w') as merged_file:
                    for dataset_type, file_path in file_paths:
                        logger.info(f"Adding content from {file_path}")
                        with open(file_path, 'r') as input_file:
                            content = input_file.read()
                            merged_file.write(content)
                            if not content.endswith('\n'):
                                merged_file.write('\n')
            else:
                logger.info(f"Skipping {file_name} as it doesn't exist in all dataset directories")


class TransformerFinder:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    @staticmethod
    def __get_transformers_classes(working_sub: List[SqlMatchingProcessor]) -> Set[Type[SqlMatchingProcessor]]:
        return set(map(lambda p: p.__class__, working_sub))

    def __calc_rea_score(self, ds_conf: DatasetConfig, working_sub: List[SqlMatchingProcessor]) -> int:
        if working_sub is None:
            return 0
        rea = RelaxedExecAcc("rea", ds_conf)
        rea_procs = self.__get_transformers_classes(rea.detector.processors)
        working_procs = self.__get_transformers_classes(working_sub)
        return 1 if working_procs.issubset(rea_procs) else 0

    def run_for_conf(self, conf: SingleRunConfig):
        if file_exists_not_forced(conf.get_trs_path()):
            logger.info(f"Repair file exists: {conf.get_trs_path()}, skipping")
            return

        detector = TransformerDetector(conf.dataset_config, [
            LetterCasingTransformer(),
            IgnoreListOrderMatcher(),
            IgnoreColOrderMatcher(),
            ExtraColumnsMatcher(),
            ExtraTupleMatcher(),
            MissingColumnsMatcher()
        ])
        ea = ExecAcc("ea", conf.dataset_config)
        gne = GoldNotEmpty("gne", conf.dataset_config)
        reader = PredGoldReader(conf)
        data = reader.get_pred_gold_db_id()
        repairs = []
        stats = {
            "count": 0,
            "ea": 0,
            "repaired": 0
        }
        for idx, (pred_str, gold_str, db_id) in tqdm(enumerate(data), desc=f"Finding transformer for {conf}",
                                                     leave=False, position=1, total=len(data)):
            pred = SqlInputData(db_id, pred_str)
            gold = SqlInputData(db_id, gold_str)
            working_sub = detector.find_working_sub_sync(pred, gold)

            ea_score = ea.calc(gold_str, pred_str, db_id)
            gold_is_empty = 1 - gne.calc(gold_str, pred_str, db_id)
            stats["count"] += 1

            if ea_score == 1:
                stats["ea"] += 1

            if ea_score == 0 and working_sub is not None:
                stats["repaired"] += 1
                messages = list(map(lambda e: e.msg(), working_sub))
                repairs.append({
                    "db_id": db_id,
                    "pred": pred.sql,
                    "gold": gold.sql,
                    "messages": messages,
                    "ea": ea_score,
                    "GOLD_IS_EMPTY": gold_is_empty
                })
        df = pd.DataFrame(repairs)
        df.to_csv(conf.get_trs_path())
        write_json(f"{conf.get_trs_path()}.json", repairs)
        write_json(f"{conf.get_trs_path()}.stats.json", stats)

    @log("Finding repairs")
    def run(self):
        run_confs = self.__config.eval_conf.get_run_confs()
        exec_multi_process(self.run_for_conf, run_confs, desc="Finding transformers")

    def post_process(self):
        merge_trs_files(self.__config)
        # dfs = []
        # for conf in self.__config.eval_conf.get_run_confs():
        #     df = pd.read_csv(conf.get_trs_path(), index_col=0)
        #     df['tmp'] = conf.temp
        #     df['itr'] = conf.itr
        #     dfs.append(df)
        # final = pd.concat(dfs, axis=0, ignore_index=True)
        # final = final[(final['ea'] == 0) & (final['rea'] == 1)]
        # final.to_csv(self.__config.eval_conf.get_trs_result_path())
