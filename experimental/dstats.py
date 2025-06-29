import json
import os


def read_data(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def get_db_ids(path: str):
    data = read_data(path)
    db_ids = set(map(lambda r: r['db_id'], data))
    return db_ids


def check_conf(dataset: str):
    train_path = os.path.join("data", dataset, "data.train.json")
    test_path = os.path.join("data", dataset, "data.test.json")
    test_db_ids = get_db_ids(test_path)
    train_db_ids = get_db_ids(train_path)
    print(f"DB Type: {dataset}")
    print(f"Test size: {len(read_data(test_path))}")
    print(f"Train size: {len(read_data(train_path))}")
    print(f"Test DBs: {len(test_db_ids)}")
    print(f"Train DBs: {len(train_db_ids)}")
    print(f"Total DBs: {len(test_db_ids) + len(train_db_ids)}")
    print(f"Inter Size: {len(test_db_ids.intersection(train_db_ids))}")
    print(f"Inter: {test_db_ids.intersection(train_db_ids)}")


def main():
    check_conf('spider')
    check_conf('bird')
    check_conf('beaver')


if __name__ == '__main__':
    main()
