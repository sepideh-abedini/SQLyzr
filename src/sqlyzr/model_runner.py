import os
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

from loguru import logger

from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.model_eval_config import ModelEvalConfig
from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.dummy_predictor import DummyPredictor
from src.third_party.dail.dail_pred import DailPredictor
from src.third_party.din.din_bird_pred import DinBirdPredictor
from src.third_party.din.din_spider_pred import DinPredictor
from src.util.async_utils import apply_async
from src.util.log_util import log, alog

RUNNER_THREADS = int(os.environ.get("RUNNER_THREADS", 1))


class ModelRunner(ABC):
    @alog("Model execution")
    async def run_single(self, run_conf: SingleRunConfig):
        logger.info(f"Running model for conf: {run_conf}")
        await self.run_single_internal(run_conf)
        logger.info(f"Finished prediction: {run_conf.get_pred_path()}")

    @abstractmethod
    async def run_single_internal(self, run_conf: SingleRunConfig):
        pass


class DailRunner(ModelRunner):

    async def run_single_internal(self, run_conf: SingleRunConfig):
        predictor = DailPredictor(run_conf)
        await predictor.run()


class DinRunner(ModelRunner):
    async def run_single_internal(self, run_conf: SingleRunConfig):
        if run_conf.dataset_config.dataset_type == "bird":
            predictor = DinBirdPredictor(run_conf)
        else:
            predictor = DinPredictor(run_conf)
        result = await predictor.run()
        return result


class DummyRunner(ModelRunner):
    async def run_single_internal(self, run_conf: SingleRunConfig):
        predictor = DummyPredictor(run_conf)
        result = await predictor.run()
        return result


MODELS = {
    "din": DinRunner(),
    "dail": DailRunner(),
    "dum": DummyRunner()
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

        # Get the base directory for this model
        model_base_dir = os.path.join(config.eval_conf.pred_dir, model)

        # Find all files in each dataset directory
        all_files = {}
        for dataset_type in dataset_types:
            dataset_dir = os.path.join(model_base_dir, dataset_type)
            if os.path.exists(dataset_dir):
                all_files[dataset_type] = [f for f in os.listdir(dataset_dir) if
                                           os.path.isfile(os.path.join(dataset_dir, f))]

        # Find common file patterns across dataset directories
        file_groups = defaultdict(list)
        for dataset_type, files in all_files.items():
            for file in files:
                # Add the full path to the file group
                file_groups[file].append((dataset_type, os.path.join(model_base_dir, dataset_type, file)))

        # Use the model base directory for merged files, which is at the same level as dataset directories
        merged_dir = model_base_dir

        # Merge files with the same name
        for file_name, file_paths in file_groups.items():
            # Only merge if the file exists in all dataset directories
            if len(file_paths) == len(dataset_types):
                merged_file_path = os.path.join(merged_dir, file_name)
                logger.info(f"Merging {len(file_paths)} files into {merged_file_path}")

                # Create the merged file
                with open(merged_file_path, 'w') as merged_file:
                    for dataset_type, file_path in file_paths:
                        logger.info(f"Adding content from {file_path}")
                        with open(file_path, 'r') as input_file:
                            content = input_file.read()
                            merged_file.write(f"--- {dataset_type} ---\n")
                            merged_file.write(content)
                            if not content.endswith('\n'):
                                merged_file.write('\n')
                            merged_file.write('\n')
            else:
                logger.info(f"Skipping {file_name} as it doesn't exist in all dataset directories")


async def run_model(config: SQLyzrConfig):
    for run_conf in config.eval_conf.get_run_confs():
        model_runner = MODELS[run_conf.model]
        await model_runner.run_single(run_conf)

    # merge_pred_files(config)
