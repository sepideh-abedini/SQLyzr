import json
import os


def get_db_ids(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    db_ids = set(map(lambda r: r['db_id'], data))
    return db_ids


train_dbs = {
    'csail_stata_neutron'
}


def check_conf(dataset: str):
    with open(os.path.join("data", dataset, "data.all.json"), 'r') as f:
        data = json.load(f)

    trains = []
    tests = []
    counts = dict()
    for r in data:
        counts[r['db_id']] = counts.setdefault(r['db_id'], 0) + 1
        if r['db_id'] in train_dbs:
            trains.append(r)
        else:
            tests.append(r)
    print(f"Tests: {len(tests)}")
    print(f"Trains: {len(trains)}")
    print(counts)
    print(len(counts))

    with open(os.path.join("data", dataset, "data.train.json"), 'w') as f:
        f.write(json.dumps(trains, indent=4))

    with open(os.path.join("data", dataset, "data.test.json"), 'w') as f:
        f.write(json.dumps(tests, indent=4))
    # test_db_ids = get_db_ids(os.path.join("data", dataset, "data.test.json"))
    # train_db_ids = get_db_ids(os.path.join("data", dataset, "data.train.json"))
    # print(f"DB Type: {dataset}")
    # print(f"Test DBs: {len(test_db_ids)}")
    # print(f"Train DBs: {len(train_db_ids)}")
    # print(f"Total DBs: {len(test_db_ids) + len(train_db_ids)}")
    # print(f"Inter Size: {len(test_db_ids.intersection(train_db_ids))}")
    # print(f"Inter: {test_db_ids.intersection(train_db_ids)}")


def main():
    # check_conf('spider')
    # check_conf('bird')
    check_conf('beaver')


if __name__ == '__main__':
    main()
