import json
import os.path
import shutil
from abc import abstractmethod, ABC
from os import path


class Transformer(ABC):

    def __init__(self, in_dir, out_dir):
        self.in_dir = in_dir
        self.out_dir = out_dir

    @abstractmethod
    def transform_json_entry(self, entry):
        pass

    @abstractmethod
    def transform_txt_entry(self, entry):
        pass

    def transform_file(self, in_path, out_path, entry_transformer):
        with open(in_path, 'r') as in_file, open(out_path, 'w') as out_file:
            in_data = json.load(in_file)
            list = []
            for entry in in_data:
                list.append(entry_transformer(entry))
            out_file.write(json.dumps(list, indent=4))

    @abstractmethod
    def transform_table(self):
        pass


    def call_transformers(self, dataset_dir: str):
        self.transform_query(dataset_dir)
        self.transform_table(dataset_dir)
        self.transform_database(dataset_dir)
