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

class DinRunner(ModelRunner):

    def run_model_single_time(self, k):
        k_dataset_dir = f"{self.dataset_dir}_{k}/"
        k_output_path = f"{self.output_dir}_{k}"
        DIN_command = f"python3 {DIN_FILE} --dataset {k_dataset_dir} --output {k_output_path} --temp {self.temp}"
        execute_command(DIN_command)



# def main():
#     runner = DinRunner(dataset_dir="data/dataset/data", output_dir="data/dataset/output_results/din", thread_count=8,
#                        temp=1)
#     runner.run()
#     runner.merge_results()
#
# if __name__ == '__main__':
#     main()
