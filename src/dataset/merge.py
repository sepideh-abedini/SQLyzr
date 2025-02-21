import argparse
import os
import shutil
from typing import List, Tuple

from src.configs.datasets import DatasetName, DatasetSize, DATASETS
from src.eval.dataset_config import DatasetConfig
from src.util.file_utils import concat_jsons, concat_files


def merge_datasets(datasets: List[Tuple[DatasetName, DatasetSize]], out_dir: str):
    confs: List[DatasetConfig] = []
    for (name, size) in datasets:
        confs.append(DATASETS[name][size])

    new_conf = DatasetConfig(
        dataset_dir=out_dir,
        test_file="all.json",
        gold_file="all.gold.txt",
        tables_file="tables.json",
        db_dir="database"
    )
    os.makedirs(new_conf.dataset_dir, exist_ok=True)
    for conf in confs:
        conf.get_test_path()
        shutil.copytree(conf.get_db_path(), new_conf.get_db_path(), dirs_exist_ok=True)
    concat_jsons(map(lambda c: c.get_test_path(), confs), new_conf.get_test_path())
    concat_jsons(map(lambda c: c.get_tables_path(), confs), new_conf.get_tables_path())
    concat_files(map(lambda c: c.get_gold_path(), confs), new_conf.get_gold_path())


def main(datasets: List[str], out_dir: str):
    pairs = []
    if len(datasets) % 2 != 0:
        raise RuntimeError(f"Invalid number of dataset args: {len(datasets)}")
    for i in range(0, len(datasets), 2):
        pairs.append((datasets[i], datasets[i + 1]))
    merge_datasets(pairs, out_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datasets", nargs="+", required=True)
    parser.add_argument("-o", "--out_dir", required=True, type=str)
    args = parser.parse_args()
    main(args.datasets, args.out_dir)
