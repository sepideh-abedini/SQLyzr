import subprocess
from abc import ABC, abstractmethod


def execute_command(command: str):
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='\n')
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)



class ModelRunner(ABC):

    @abstractmethod
    def run(self, dataset_dir, output_dir, temp):
        pass

