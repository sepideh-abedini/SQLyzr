import json
import shutil

from tqdm import tqdm

from src.cat.catter import Catter
from src.configs.sqlyzr import SQLyzrConfig
from src.dataset.models import SpiderExample
from src.eval.exact_match import ExactMatchParser
from src.eval.lib import DatabaseClient
from src.eval.model_eval_config import ModelEvalConfig
from src.util.logger import log
from loguru import logger


# FIXME
def validate_dataset(conf: SQLyzrConfig):
    catter = Catter()
    errors = []
    total = 0
    valid_examples = []
    data_file_path = conf.eval_conf.dataset_config.get_data_path()
    with open(data_file_path) as file:
        data = json.load(file)
        for i, entry in tqdm(enumerate(data), colour="green", total=len(data),
                             desc=f"Validating dataset: {conf.eval_conf.dataset_config.dataset_dir}"):
            example = SpiderExample.model_validate(entry)
            cat = catter.get_category(example.query)
            dbc = DatabaseClient(conf.eval_conf.dataset_config)
            exec_res = dbc.exec_sql(example.db_id, example.query)
            if exec_res is None or cat is None:
                errors.append((i, example.query))
            else:
                valid_examples.append(entry)
            total += 1

    with open(f"{data_file_path}.err", "w") as errors_file:
        for error in errors:
            errors_file.write(f"{error}\n")

    if len(errors) > 0:
        logger.debug("Invalid SQLs found!")
        logger.debug(f"Num dataset errors: {len(errors)}/{total}")
        logger.debug(f"Removing invalid entries, backup is saved in f{data_file_path}.bak")
        with open(f"data_file_path.clean", "w") as out_file:
            out_file.write(json.dumps(valid_examples, indent=True))
        raise RuntimeError("Invalid dataset")
    else:
        logger.info("Dataset is valid!")


def validate_preds(conf: ModelEvalConfig):
    parser = ExactMatchParser(conf.dataset_config.get_tables_path())
    for run_conf in conf.get_run_confs():
        errors = []
        with (open(run_conf.dataset_config.get_data_path()) as data_file,
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
