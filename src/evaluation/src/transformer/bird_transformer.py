import json
from os import path

from src.transformer.transformer import Transformer


class BirdTransformer(Transformer):

    def transform_query(self, bird_dir: str):
        train_path = path.join(bird_dir, "dev.json")
        queries_out_path = path.join(self.out_dir ,'dev.json')

        with open(train_path, 'r') as in_file, open(queries_out_path, 'w') as out_file:
            train_data = json.load(in_file)
            list = []
            for line in train_data:
                list.append({
                    "db_id": line["db_id"],
                    "query": line["SQL"],
                    "question": line["question"],
                    "evidence": line["evidence"],
                })

            out_file.write(json.dumps(list, indent=4))

    def transform_table(self, bird_dir: str):
        table_path = path.join(bird_dir, "tables.json")
        tables_out_path = path.join(self.out_dir ,'tables.json')

        with open(table_path, 'r') as in_file, open(tables_out_path, 'w') as out_file:
            table = json.load(in_file)

            out_file.write(json.dumps(table, indent=4))




def main():
    transformer = BirdTransformer('dataset/data')
    transformer.call_transformers("dataset/bird")



if __name__ == '__main__':
        main()
