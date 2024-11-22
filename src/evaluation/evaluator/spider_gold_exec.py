import json
import os.path

from tqdm import tqdm

from din_model_evaluator import exec_sql


def gold_exec(gold_path, db_dir):
    count = 0
    with open(gold_path, 'r') as f:
        file = json.load(f)
        for line in tqdm(file):
            db = os.path.join(db_dir, line['db_id'], f'{line['db_id']}.sqlite')
            res = exec_sql(db, line['query'])

            if res == False:
                count += 1
    return count




def main():
    # with open('data/dataset/spider/train_others.json') as f1:
    #     d1 = json.load(f1)
    # with open('data/dataset/spider/train_spider.json') as f2:
    #     d2 = json.load(f2)
    # with open('data/dataset/spider/dev.bak.json') as f3:
    #     d3 = json.load(f3)
    # full = d1 + d2 + d3
    # with open('data/dataset/spider/dev.json', 'w') as f:
    #     json.dump(full, f, indent=4)
    # print(len(full))
    num_failures1 = gold_exec('data/dataset/spider/train_others.json', 'data/dataset/spider/database')
    num_failures2 = gold_exec('data/dataset/spider/dev.bak.json', 'data/dataset/spider/database')
    num_failures3 = gold_exec('data/dataset/spider/train_spider.json', 'data/dataset/spider/database')
    print("Num Failures:\n", num_failures1)
    print("Num Failures:\n", num_failures2)
    print("Num Failures:\n", num_failures3)


if __name__ == '__main__':
    main()
