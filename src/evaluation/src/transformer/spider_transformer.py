import json
from os import path
import shutil

from src.evaluation.src.transformer.transformer import Transformer


class SpiderTransformer(Transformer):

    def transform_query(self, spider_dir:str):
        train_path = path.join(spider_dir, "train_spider.json")
        queries_out_path = path.join(self.out_dir ,'dev.json')

        with open(train_path, 'r') as in_file, open(queries_out_path, 'w') as out_file:
                train_data = json.load(in_file)
                list = []
                for line in train_data:
                    list.append({
                        "db_id" : line["db_id"],
                        "query" : line["query"],
                        "question" : line["question"],
                        "evidence" : "",
                    })

                out_file.write(json.dumps(list, indent=4))

        dev_path = path.join(spider_dir ,'train_spider.json')
        gold_out_path = path.join(self.out_dir ,'gold.txt')

        with open(dev_path, 'r') as in_file, open(gold_out_path, 'w') as out_file:
            dev_data = json.load(in_file)
            list = []
            for line in dev_data:
                list.append(f"{line['query']}\t{line["db_id"]}\n")

            for line in list:
                out_file.write(line)

    def transform_table(self, spider_dir:str):
        table_path = path.join(spider_dir, "tables.json")
        tables_out_path = path.join(self.out_dir ,'tables.json')
        with open(table_path, 'r') as in_file, open(tables_out_path, 'w') as out_file:
            table = json.load(in_file)

            out_file.write(json.dumps(table, indent=4))


def main():
    transformer = SpiderTransformer('data/dataset/data')
    transformer.call_transformers("data/dataset/spider")



if __name__ == '__main__':
        main()

