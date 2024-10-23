import shutil
from abc import abstractmethod, ABC
from os import path

class Transformer(ABC):

    def __init__(self, out_dir):
        self.out_dir = out_dir

    @abstractmethod
    def transform_query(self, dataset_dir: str):
        pass

    @abstractmethod
    def transform_table(self, dataset_dir: str):
        pass

    def transform_database(self, spider_dir: str):
        database_path = path.join(spider_dir, "database")
        database_out_path = path.join(self.out_dir ,'database')

        # Copy the directory
        shutil.copytree(database_path, database_out_path)

    def call_transformers(self, dataset_dir: str):
        self.transform_query(dataset_dir)
        self.transform_table(dataset_dir)
        self.transform_database(dataset_dir)


