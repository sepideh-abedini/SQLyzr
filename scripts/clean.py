#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import shutil

from tqdm import tqdm

from src.cat.catter import Catter
from src.dataset.models import SpiderExample
from src.rel.db_facade import DatabaseFacade

from loguru import logger


async def clean_dataset(file_path: str, db_path: str):
    catter = Catter()
    errors = []
    total = 0
    valid_examples = []
    data_file_path = file_path
    with open(data_file_path) as file:
        data = json.load(file)
        for i, entry in tqdm(enumerate(data), colour="green", total=len(data),
                             desc=f"Validating dataset: {data_file_path}"):
            example = SpiderExample.model_validate(entry)
            cat = catter.get_category(example.query)
            db_facade = DatabaseFacade(db_path)
            exec_res = await db_facade.exec_query_async(example.db_id, example.query)
            if exec_res is None or cat is None:
                errors.append((i, example.query))
            else:
                valid_examples.append(entry)
            total += 1

    with open(f"{data_file_path}.err", "w") as errors_file:
        for error in errors:
            errors_file.write(f"{error}\n")

    if len(errors) > 0:
        logger.info("Invalid SQLs found!")
        logger.info(f"Num dataset errors: {len(errors)}/{total}")
        file_stem = os.path.splitext(data_file_path)[0]
        shutil.copy(data_file_path, f"{file_stem}.dirty.json")
        logger.info(f"Copied data file to {file_stem}.dirty.json")
        with open(f"{data_file_path}", "w") as out_file:
            out_file.write(json.dumps(valid_examples, indent=True))
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
