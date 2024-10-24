from abc import ABC
import subprocess
from src.evaluation.src.models_runner.runner import ModelRunner, execute_command


DIN_FILE = 'src/models/din/DIN-SQL.py'



class DinRunner(ModelRunner):

    def run(self, dataset_dir, output_dir, temp):
        # temp = 1
        DIN_command = f"python3 {DIN_FILE} --dataset {dataset_dir} --output {output_dir} --temp {temp}"
        execute_command(DIN_command)

def main():
    runner = DinRunner()
    runner.run("dataset/data/", "dataset/output_results/din", 1)


if __name__ == '__main__':
    main()
