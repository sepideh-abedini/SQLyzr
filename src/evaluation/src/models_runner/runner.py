import json
import math
import os
import shutil
import subprocess
import threading
from abc import ABC, abstractmethod
from pathlib import Path

import tqdm
from attr import dataclass


def execute_command(command: str):
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        output, errors = p.communicate()
        print(output, errors)
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)


@dataclass
class ModelRunner(ABC):
    dataset_dir: str
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
        with (open(os.path.join(self.dataset_dir, "dev.json"), 'r') as file):
            data = json.load(file)
            data_len = len(data)
            chunk_size = math.ceil(data_len / self.thread_count)

            for i in range(self.thread_count):
                start = i * chunk_size
                end = start + chunk_size
                chunked = data[start:end]

                dataset_parent_dir = Path(self.dataset_dir).parent
                dataset_chunk_dir = f"{dataset_parent_dir}/data_{i}"
                shutil.copytree(self.dataset_dir, dataset_chunk_dir, dirs_exist_ok=True)
                dev_json_chunk_path = os.path.join(dataset_chunk_dir, "dev.json")
                with open(dev_json_chunk_path, 'w') as out_file:
                    json.dump(chunked, out_file, indent=4)

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

