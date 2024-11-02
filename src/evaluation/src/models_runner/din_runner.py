import json
import math
import os.path
import shutil
import threading
from dataclasses import dataclass
from pathlib import Path

from fontTools.afmLib import readlines

from src.evaluation.src.models_runner.runner import ModelRunner, execute_command

DIN_FILE = 'src/models/din/DIN-SQL.py'


@dataclass
class DinRunner(ModelRunner):
    dataset_dir: str
    output_dir: str
    thread_count: int
    temp: int

    def run(self):
        threads = []
        self.split_dataset()

        for k in range(self.thread_count):
            thread = threading.Thread(target=self.run_model_single_time, args=(k,))
            thread.start()
            threads.append(thread)

        for thread in threads:
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

    def run_model_single_time(self, k):
        k_dataset_dir = f"{self.dataset_dir}_{k}/"
        k_output_path = f"{self.output_dir}/output_{k}"
        DIN_command = f"python3 {DIN_FILE} --dataset {k_dataset_dir} --output {k_output_path} --temp {self.temp}"
        execute_command(DIN_command)

    def merge_results(self):
        all_toks = 0
        with open (f"{self.output_dir}/results.txt", 'w') as out:
            for i in range(self.thread_count):
                with open(f"{self.output_dir}/output_{i}", 'r') as file:
                    count_lines = file.readlines()
                    last_line = count_lines[-1]
                    toks = int(last_line.split(":")[-1])
                    all_toks += toks

                    out.writelines(count_lines[:-1])
            out.write(f"tokens:{all_toks}")


def main():
    runner = DinRunner(dataset_dir="data/dataset/data", output_dir="data/dataset/output_results/din", thread_count=8,
                       temp=1)
    # runner.run()
    runner.merge_results()

if __name__ == '__main__':
    main()
