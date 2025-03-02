#!/usr/bin/env python3
import argparse
import json
import os
import shutil

from loguru import logger
from tqdm import tqdm

from src.cat.catter import Catter
from src.configs.config_loader import load_config
from src.dataset.models import SpiderExample
from src.eval.dataset_config import DatasetConfig
from src.rel.db_facade import DatabaseFacade
from src.rel.db_factory import DatabaseFactory
from src.util.log_util import configure_logging
from src.util.multi_thread_utils import exec_multi_process


class SqlExecWorker:
    db_facade: DatabaseFacade

    def __init__(self, config):
        self.db_facade = DatabaseFactory.get_instance(config)

    def exec(self, ex):
        r = self.db_facade.exec_query_sync(ex.db_id, ex.query)
        return r

    def exec_for_examples(self, data):
        res = []
        for ex in tqdm(data, desc=f"[{os.getpid()}]: Executing queries", total=len(data)):
            r = self.exec(ex)
            res.append(r)
        return res


def clean_file(dataset_conf: DatasetConfig, data_file_path: str, overwrite: bool):
    db_facade = DatabaseFactory.get_instance(dataset_conf)
    catter = Catter()
    errors = []
    total = 0
    valid_examples = []
    with open(data_file_path) as file:
        data = json.load(file)
        # data = data[4000:4500]
        examples = []
        for i, entry in enumerate(data):
            example = SpiderExample.model_validate(entry)
            example.idx = i
            examples.append(example)

        worker = SqlExecWorker(dataset_conf)
        #
        results = exec_multi_process(worker.exec, examples)
        # results = list(tqdm(map(worker.exec, examples),total=len(examples)))

        for i, entry in tqdm(enumerate(data), colour="green", total=len(data),
                             desc=f"Validating dataset: {dataset_conf.dataset_type}"):
            entry['query'] = entry['query'].replace("\n", " ")
            example = SpiderExample.model_validate(entry)
            cat = catter.get_category(example.query)
            exec_res = results[i]
            if exec_res is None:
                errors.append((i, example.db_id, 'EXEC_ERROR', example.query))
            elif cat is None:
                errors.append((i, example.db_id, 'PARSE_ERROR', example.query))
            else:
                valid_examples.append(entry)
            total += 1

    with open(f"{data_file_path}.err", "w") as errors_file:
        for error in errors:
            errors_file.write(f"{error}\n")

    if len(errors) > 0:
        logger.info("Invalid SQLs found!")
        logger.info(f"Num dataset errors: {len(errors)}/{total}")
        logger.info(f"Num timeout errors: {len(list(filter(lambda x: x[2] == 'TIMEOUT', errors)))}")
        logger.info(f"Num parser errors: {len(list(filter(lambda x: x[2] == 'PARSER_ERROR', errors)))}")
        logger.info(f"Num exec errors: {len(list(filter(lambda x: x[2] == 'EXEC_ERROR', errors)))}")
        file_stem = os.path.splitext(data_file_path)[0]
        shutil.copy(data_file_path, f"{file_stem}.dirty.json")
        logger.info(f"Copied data file to {file_stem}.dirty.json")

        if overwrite:
            with open(f"{data_file_path}", "w") as out_file:
                out_file.write(json.dumps(valid_examples, indent=True))

        with open(f"{file_stem}.errors.json", "w") as out_file:
            out_file.write(json.dumps(errors, indent=True))

        logger.info(f"Invalid examples removed!")
    else:
        logger.info("Dataset is valid!")


def clean_dataset(config_path: str, overwrite: bool):
    conf = load_config(config_path)
    dataset_conf = conf.eval_conf.dataset_config
    clean_file(dataset_conf, dataset_conf.get_train_path(), overwrite)
    clean_file(dataset_conf, dataset_conf.get_test_path(), overwrite)


def main(config_file, overwrite):
    clean_dataset(config_file, overwrite)


if __name__ == '__main__':
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", required=True, help="Config file")
    parser.add_argument("-f", required=False, action='store_true', default=False, help="Overwrite")
    args = parser.parse_args()
    main(args.c, args.f)
