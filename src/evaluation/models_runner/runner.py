import json
import math
import os
import shutil
import threading
from abc import ABC, abstractmethod

import tqdm
from attr import dataclass

from src.evaluation.src.models_runner.run_config import ModelEvalConfig


@dataclass
class ModelRunner(ABC):
    config: ModelEvalConfig
    output_dir: str
    thread_count: int
    temp: float

    def run(self):
        threads = []
        self.split_dataset()

        for k in range(self.thread_count):
            thread = threading.Thread(target=self.run_model_single_time, args=(k,))
            thread.start()
            threads.append(thread)

        for thread in tqdm.tqdm(threads):
            thread.join()

    def split_dataset(self):
        with (open(self.config.get_query_file_path(), 'r') as file):
            data = json.load(file)
            data_len = len(data)
            chunk_size = math.ceil(data_len / self.thread_count)

            for i in range(self.thread_count):
                start = i * chunk_size
                end = start + chunk_size
                chunked = data[start:end]

                dataset_chunk_dir = self.config.get_chunk_path(i)
                shutil.copytree(self.config.dataset_path, dataset_chunk_dir, dirs_exist_ok=True)
                dev_json_chunk_path = os.path.join(dataset_chunk_dir, self.config.query_file)
                with open(dev_json_chunk_path, 'w') as out_file:
                    json.dump(chunked, out_file, indent=4)
                gold_txt_chunk_path = os.path.join(dataset_chunk_dir, self.config.gold_file)
                with open(gold_txt_chunk_path, 'w') as out_file:
                    out_file.writelines("\n".join(list(map(lambda data: f"{data["query"]}\t{data["db_id"]}", chunked))))

    @abstractmethod
    def run_model_single_time(self, k):
        pass

    def merge_results(self):
        all_toks = 0
        with open(f"{self.output_dir}", 'w') as out:
            for i in range(self.thread_count):
                with open(f"{self.output_dir}_{i}", 'r') as file:
                    count_lines = file.readlines()
                    last_line = count_lines[-1]
                    toks = int(last_line.split(":")[-1])
                    all_toks += toks

                    out.writelines(count_lines[:-1])
            out.write(f"tokens:{all_toks}")
