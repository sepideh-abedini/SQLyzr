#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import shutil

from loguru import logger
from tqdm import tqdm

from src.cat.catter import Catter
from src.configs.datasets import SPIDER_ALL
from src.dataset.models import SpiderExample
from src.rel.db_facade import DatabaseFactory
from src.util.multi_thread_utils import exec_multi_thread


async def clean_dataset(file_path: str, db_path: str):
    db_facade = DatabaseFactory.get_instance(SPIDER_ALL)
    catter = Catter()
    errors = []
    total = 0
    valid_examples = []
    data_file_path = file_path
    with open(data_file_path) as file:
        data = json.load(file)
        examples = []
        for i, entry in enumerate(data):
            example = SpiderExample.model_validate(entry)
            example.idx = i
            examples.append(example)

        def exec_for_examples(data):
            res = []
            for ex in data:
                r = db_facade.exec_query_sync(ex.db_id, ex.query)
                res.append(r)
            return res

        results = exec_multi_thread(exec_for_examples, examples)

        for i, entry in tqdm(enumerate(data), colour="green", total=len(data),
                             desc=f"Validating dataset: {db_path}"):
            example = SpiderExample.model_validate(entry)
            cat = catter.get_category(example.query)
            exec_res = results[i]
            if isinstance(exec_res, asyncio.TimeoutError):
                errors.append((i, example.db_id, 'TIMEOUT', example.query))
            elif exec_res is None:
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

        with open(f"{data_file_path}", "w") as out_file:
            out_file.write(json.dumps(valid_examples, indent=True))

        with open(f"{file_stem}.errors.json", "w") as out_file:
            out_file.write(json.dumps(errors, indent=True))

        logger.info(f"Invalid examples removed!")
    else:
        logger.info("Dataset is valid!")


async def main(data_file, db_dir):
    await clean_dataset(data_file, db_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", required=True, help="Data file")
    parser.add_argument("-d", required=True, help="Database dir")
    args = parser.parse_args()
    asyncio.run(main(args.f, args.d))
