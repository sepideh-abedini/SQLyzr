import os
from collections import defaultdict

from loguru import logger

from src.configs.sqlyzr_config import SQLyzrConfig
from src.model.custom_runner import CustomRunner
from src.sqlyzr.model_runner import DinRunner, DailRunner, DummyRunner

MODELS = {
    "din": DinRunner(),
    "dail": DailRunner(),
    "dum": DummyRunner(),
    "custom": CustomRunner()
}


def merge_pred_files(config: SQLyzrConfig):
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

        model_base_dir = os.path.join(config.eval_conf.pred_dir, model)

        all_files = {}
        for dataset_type in dataset_types:
            dataset_dir = os.path.join(model_base_dir, dataset_type)
            if os.path.exists(dataset_dir):
                all_files[dataset_type] = []
                for f in os.listdir(dataset_dir):
                    p = os.path.join(dataset_dir, f)
                    if os.path.isfile(p) and p.endswith('.txt'):
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


async def run_model(config: SQLyzrConfig):
    for run_conf in config.eval_conf.get_run_confs():
        model_runner = MODELS[run_conf.model]
        await model_runner.run_single(run_conf)

    merge_pred_files(config)
