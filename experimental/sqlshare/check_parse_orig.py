from src.configs.datasets import SPIDER_ALL, BIRD_ALL, BEAVER_ALL
from src.parse.parser import SqlParser
from src.util.file_utils import read_json
from src.util.log_util import configure_logging

configure_logging()

def check_data(path):
    data = read_json(path)

    parser = SqlParser()

    e = 0
    for row in data:
        sql = row['query']
        ast = parser.parse(sql)
        if not ast:
            e += 1
            print(sql)
    print(f"{path}: {e}/{len(data)}")


for path in [
    SPIDER_ALL.get_test_path(),
    SPIDER_ALL.get_train_path(),
    BIRD_ALL.get_test_path(),
    BIRD_ALL.get_train_path(),
    BEAVER_ALL.get_train_path(),
    BEAVER_ALL.get_test_path()
]:
    check_data(path)
