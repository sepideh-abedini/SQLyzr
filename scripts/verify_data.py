import tqdm
import argparse
from dotenv import load_dotenv

from src.cat.catter import Catter
from src.eval.dataset_config import DatasetConfig
from src.util.log_util import configure_logging

load_dotenv()
configure_logging()
from src.db.db_factory import DatabaseFactory
from src.util.file_utils import read_json

from src.configs.datasets import DATASETS


def verify_ds(d: DatasetConfig):
    catter = Catter()
    print(f"Dataset dir: {d}")
    test_data = read_json(d.get_test_path())
    print("\tTest size: ", len(test_data))
    train_data = read_json(d.get_train_path())
    print("\tTrain size: ", len(train_data))
    all_data = test_data + train_data
    dbf = DatabaseFactory.get_instance(d)
    test_db_ids = set(map(lambda x: x['db_id'], test_data))
    train_db_ids = set(map(lambda x: x['db_id'], train_data))
    assert len(test_db_ids.intersection(train_db_ids)) == 0
    print("Common dbs:", test_db_ids.intersection(train_db_ids))
    for r in tqdm.tqdm(all_data, total=len(all_data)):
        sql = r['query']
        res = dbf.exec_query_sync(r['db_id'], sql)
        cat = catter.get_category(sql)
        assert res is not None
        assert cat is not None

    table_data = read_json(d.get_tables_path())
    all_db_ids = set(map(lambda x: x['db_id'], table_data))
    table_db_ids = set(map(lambda x: x['db_id'], table_data))
    assert all_db_ids.issubset(table_db_ids)

    return len(train_data), len(test_data)


def main(dataset: str, size: str):
    ds = DATASETS[dataset][size]

    total_test = 0
    total_train = 0
    for d in ds:
        train_size, test_size = verify_ds(d)
        total_train += train_size
        total_test += test_size

    print(f"Total test size: {total_test}")
    print(f"Total train size: {total_train}")
    print(f"Total size: {total_test + total_train}")

    print("\033[1;32mdata is valid\033[0m")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", type=str, required=True)
    parser.add_argument("-s", type=str, required=True)
    args = parser.parse_args()
    main(args.d, args.s)
