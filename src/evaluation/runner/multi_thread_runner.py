import json
import math
import shutil
from dataclasses import dataclass, replace
from typing import List, Type

from src.evaluation.runner.dail_runner import DailRunner
from src.evaluation.runner.dataset_config import SPIDER_SMALL
from src.evaluation.runner.model_runner import ModelRunner
from src.evaluation.runner.runner_config import RunnerConfig


@dataclass
class MultiThreadRunner:
    config: RunnerConfig
    runner_type: Type[ModelRunner]
    num_threads: int

    def run(self):
        thread_configs = self.split_dataset()

        runners = []
        for config in thread_configs:
            runner = self.runner_type(config)
            runner.start()
            runners.append(runner)

        for runner in runners:
            runner.join()

        self.merge_pred_results(thread_configs)

    def merge_pred_results(self, thread_configs: List[RunnerConfig]):
        all_toks = 0
        with open(f"{self.config.output_path}", 'w') as out:
            for config in thread_configs:
                with open(config.output_path) as file:
                    count_lines = file.readlines()
                    last_line = count_lines[-1]
                    toks = int(last_line.split(":")[-1])
                    all_toks += toks

                    out.writelines(count_lines[:-1])
            out.write(f"tokens:{all_toks}")

    def split_dataset(self) -> List[RunnerConfig]:
        thread_configs = []
        for i in range(self.num_threads):
            chunk_suffix = f"chunk_{i}"
            dataset_config = replace(self.config.dataset_config,
                                     dataset_dir=f"{self.config.dataset_config.dataset_dir}_{chunk_suffix}")
            thread_config = replace(self.config, dataset_config=dataset_config,
                                    output_path=f"{self.config.output_path}_{chunk_suffix}")
            thread_configs.append(thread_config)

        for thread_config in thread_configs:
            shutil.copytree(self.config.dataset_config.dataset_dir, thread_config.dataset_config.dataset_dir,
                            dirs_exist_ok=True)

        with open(self.config.dataset_config.get_data_path()) as data_file:
            data_json = json.load(data_file)
            data_len = len(data_json)
            chunk_size = math.ceil(data_len / self.num_threads)
            print(f"Splitting data in chunk of size: {chunk_size}")
            for i in range(self.num_threads):
                start = i * chunk_size
                end = start + chunk_size
                print(f"Chunk[{i}]: {start}-{end}")
                chunk_data = data_json[start:end]
                with open(thread_configs[i].dataset_config.get_data_path(), "w") as chunk_file:
                    json.dump(chunk_data, chunk_file, indent=4)
        return thread_configs


if __name__ == "__main__":
    dataset_config = SPIDER_SMALL
    runner_config = RunnerConfig(dataset_config=SPIDER_SMALL, output_path="data/dum/pred.txt", temp=1.0)
    runner = MultiThreadRunner(runner_config, DailRunner, 4)
    runner.run()
