import json
import math
import multiprocessing
import shutil
import time
from dataclasses import dataclass, replace
from random import randrange
from typing import List, Type
from multiprocessing import Pool

# from src.evaluation.runner.dail_runner import DailRunner
from src.evaluation.runner.configs import SPIDER_SMALL, EVAL_CONF
from src.evaluation.runner.din_runner import DinRunner
from src.evaluation.runner.model_runner import ModelRunner
from src.evaluation.runner.runner_config import SingleRunConfig
from src.evaluation.runner.utils import get_chunks


@dataclass
class MultiThreadRunner:
    config: SingleRunConfig
    runner_type: Type[ModelRunner]
    num_threads: int

    def run(self):
        thread_configs = self.split_dataset()

        with Pool(self.num_threads) as p:
            for i, config in enumerate(thread_configs):
                runner = self.runner_type(config)
                p.apply_async(runner.run)
                print(f"Started process: {i}")
            p.close()
            p.join()
            print("Processes joined")

        self.merge_pred_results(thread_configs)

    def merge_pred_results(self, thread_configs: List[SingleRunConfig]):
        all_toks = 0
        lines = []
        for config in thread_configs:
            with open(config.get_pred_path()) as file:
                count_lines = file.readlines()
                last_line = count_lines[-1]
                toks = int(last_line.split(":")[-1])
                all_toks += toks
                lines.extend(count_lines[:-1])
        with open(f"{self.config.get_pred_path()}", 'w') as out:
            out.writelines(lines)
            out.write(f"tokens:{all_toks}")

    def split_dataset(self) -> List[SingleRunConfig]:
        thread_configs = []
        for i in range(self.num_threads):
            thread_config = self.config.to_thread_conf(i)
            thread_configs.append(thread_config)

        for thread_config in thread_configs:
            shutil.copytree(self.config.dataset_config.dataset_dir, thread_config.dataset_config.dataset_dir,
                            dirs_exist_ok=True)

        with open(self.config.dataset_config.get_data_path()) as data_file:
            data_json = json.load(data_file)
            data_len = len(data_json)
            chunks = get_chunks(data_len, self.num_threads)
            print(f"Splitting data in chunks: {chunks}")
            start = 0
            for i in range(self.num_threads):
                end = start + chunks[i]
                print(f"Chunk[{i}]: {start}-{end}")
                chunk_data = data_json[start:end]
                with open(thread_configs[i].dataset_config.get_data_path(), "w") as chunk_file:
                    json.dump(chunk_data, chunk_file, indent=4)
                start = end
        return thread_configs


if __name__ == "__main__":
    # runner = MultiThreadRunner(EVAL_CONF.get_runner_conf(0.0, 1), DailRunner, 2)
    runner = MultiThreadRunner(EVAL_CONF.get_runner_conf(0.0, 1), DinRunner, 8)
    # runner.split_dataset()
    runner.run()
    runner.run()
    runner.run()
