import json
from os import path
import shutil

from src.evaluation.src.transformer.transformer import Transformer


class SpiderTransformer(Transformer):

    def transform_json_entry(self, entry):
        return {
            "db_id": entry["db_id"],
            "query": entry["query"],
            "question": entry["question"],
            "evidence": "",
        }

    def transform_txt_entry(self, entry):
        return f"{entry['query']}\t{entry["db_id"]}\n"

    def transform_json_data(self, data):
        return list(map(self.transform_json_entry, data))

    def transform_query(self):
        self.transform_json_file("dev.json", "test.json")
        self.transform_json_file("train.json", "train.json")
        self.merge_jsons(path.join(self.out_dir, "test.json"),
                         path.join(self.out_dir, "train.json"),
                         path.join(self.out_dir, "all.json"))
        self.transform_gold_file("dev.json", "test.gold.txt")
        self.transform_gold_file("train.json", "train.gold.txt")
        self.merge_texts(path.join(self.out_dir, "test.gold.txt"),
                         path.join(self.out_dir, "train.gold.txt"),
                         path.join(self.out_dir, "all.gold.txt"))

    def transform_gold_file(self, in_path, out_path):
        with open(path.join(self.in_dir, in_path), "r") as in_file, open(
                path.join(self.out_dir, out_path), "w") as out_file:
            dev_json_data = json.load(in_file)
            data = list(map(self.transform_txt_entry, dev_json_data))
            out_file.writelines(data)

    def transform_json_file(self, in_path, out_path):
        with open(path.join(self.in_dir, in_path), "r") as in_file, open(
                path.join(self.out_dir, out_path), "w") as out_file:
            dev_json_data = json.load(in_file)
            dev_json_data_transformed = self.transform_json_data(dev_json_data)
            out_file.write(json.dumps(dev_json_data_transformed, indent=4))

    def transform_table(self):
        with open(path.join(self.in_dir, "tables.json"), "r") as in_file, open(
                path.join(self.out_dir, "tables.json"), "w") as out_file:
            out_file.writelines(in_file)

    def merge_jsons(self, a_path, b_path, out_path):
        with open(a_path, 'r') as dev_table_file, open(b_path, 'r') as train_table_file:
            with open(out_path, 'w') as out_file:
                dev_table_data = json.load(dev_table_file)
                train_table_data = json.load(train_table_file)
                out_file.write(json.dumps(dev_table_data + train_table_data, indent=4))

    def merge_texts(self, a_path, b_path, out_path):
        with open(a_path) as a_file, open(b_path) as b_file:
            with open(out_path, 'w') as out_file:
                out_file.write(a_file.read())
                out_file.write(b_file.read())

    def transform_database(self):
        database_path = path.join(self.in_dir, "database")
        database_out_path = path.join(self.out_dir, "database")
        shutil.copytree(database_path, database_out_path)


def main():
    transformer = SpiderTransformer('data/dataset/spider', 'data/dataset/uniform')
    transformer.transform_query()
    transformer.transform_table()
    transformer.transform_database()


if __name__ == '__main__':
    main()
