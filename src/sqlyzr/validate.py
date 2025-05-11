import json
from functools import partial
from typing import List

from loguru import logger
from tqdm import tqdm
from tqdm.asyncio import tqdm

from src.cat.catter import Catter
from src.configs.sqlyzr_config import SQLyzrConfig
from src.dataset.models import SpiderExample
from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser
from src.eval.model_eval_config import ModelEvalConfig
from src.rel.db_factory import DatabaseFactory
from src.util.file_utils import read_json
from src.util.multi_thread_utils import exec_multi_process


def exec_example(db_facade, e: SpiderExample):
    return db_facade.exec_query_sync(e.db_id, e.query)


async def validate_dataset(dataset_configs: List[DatasetConfig]):
    catter = Catter()
    errors = []
    total = 0
    valid_examples = []

    for ds_conf in dataset_configs:
        test_data = read_json(ds_conf.get_test_path())
        train_data = read_json(ds_conf.get_test_path())

        db_facade = DatabaseFactory.get_instance(ds_conf)

        db_facade.check_connection()

        logger.info(f"Validating dataset={ds_conf.dataset_type}, train={len(train_data)}, test={len(test_data)} ")

        examples = list(map(SpiderExample.model_validate, test_data))

        results = exec_multi_process(partial(exec_example, db_facade), examples, "Executing gold SQLs")

        for i, entry in tqdm(enumerate(test_data), total=len(test_data),
                             desc=f"Validating dataset: {ds_conf.dataset_dir}"):
            example = SpiderExample.model_validate(entry)
            cat = catter.get_category(example.query)
            exec_res = results[i]
            if exec_res is None or cat is None:
                errors.append((i, example.query))
            else:
                valid_examples.append(entry)
            total += 1

        with open(f"{ds_conf.get_test_path()}.err", "w") as errors_file:
            for error in errors:
                errors_file.write(f"{error}\n")

        if len(errors) > 0:
            logger.error("Invalid SQLs found!")
            logger.error(f"Num dataset errors: {len(errors)}/{total}")
            with open(f"{ds_conf.get_test_path()}.clean", "w") as out_file:
                out_file.write(json.dumps(valid_examples, indent=True))
            raise RuntimeError("Invalid dataset")
        else:
            logger.info("Dataset is valid!")


def validate_preds(conf: ModelEvalConfig):
    parser = ExactMatchParser(conf.dataset_configs.get_tables_path())
    for run_conf in conf.get_run_confs():
        errors = []
        with (open(run_conf.dataset_configs.get_test_path()) as data_file,
              open(run_conf.get_pred_path()) as pred_file):
            data = json.load(data_file)
            pred_lines = pred_file.readlines()
            for i in range(len(data)):
                pred = pred_lines[i]
                try:
                    ast = parser.parse(pred_lines[i], data[i]["db_id"])
                except Exception:
                    ast = None
                if ast is None:
                    errors.append({"pred": pred, "gold": data[i]["query"], "question": data[i]["question"]})
            with open(f"{run_conf.get_pred_path()}.errors.json", "w") as errors_file:
                errors_file.write(json.dumps(errors, indent=4))
            print(f"{run_conf.get_pred_path()} errors: {len(errors)}/{len(data)}")
