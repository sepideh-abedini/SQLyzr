import argparse
import os

import pandas as pd

from src.cat.catter import Catter
from src.configs.datasets import SPIDER_ALL
from src.util.file_utils import read_json, write_json

skip_dbs = {
    "activity_1"
}


def print_cat_dist(cat_file):
    df = pd.read_csv(cat_file)
    df = df[df['cat'] != "c1000"]
    df = df[['cat']]
    counts = df['cat'].value_counts().sort_index()
    return counts


def process_sqlyzr(file_path):
    df = pd.read_csv(file_path)
    df = df[df['dst'] == 'spider']
    df['ds_idx'] = df['dst'].astype(str) + df['ds_idx'].astype(str)
    df = df.groupby(['ds_idx'], as_index=False).first()
    df = df[['cat']]
    counts = df['cat'].value_counts().sort_index()
    return counts


def sqlyzr_uniq_questions(file_path):
    df = pd.read_csv(file_path)
    df = df[df['dst'] == 'spider']
    df['ds_idx'] = df['dst'].astype(str) + df['ds_idx'].astype(str)
    df = df.groupby(['ds_idx'], as_index=False).first()
    return df


def list_scaled_dbs():
    dbs_dir = SPIDER_ALL.get_db_path()
    scale_100_path = f"{dbs_dir}_s100"
    dbs = [d for d in os.listdir(scale_100_path) if os.path.isdir(os.path.join(scale_100_path, d))]
    return dbs


def main(in_file, sqlshare_file, out_file):
    spider_dict = dict()
    catter = Catter()

    spider_data = read_json(SPIDER_ALL.get_test_path())
    for idx, row in enumerate(spider_data):
        row['cat'] = catter.get_category(row['query']).name
        spider_dict[idx] = row
    scale_dbs = list_scaled_dbs()

    counts_sqlshare = print_cat_dist(sqlshare_file)
    counts_sqlyzr = process_sqlyzr(in_file)

    df = pd.read_csv(in_file)
    df = df[df['dst'] == 'spider']

    print("SQLyzr Total:", df.shape[0])
    print("SQLyzr Questions:", counts_sqlyzr.sum())
    print("SQLShare Questions:", counts_sqlshare.sum())

    ratios = counts_sqlyzr / counts_sqlshare
    print("Ratios:")
    print(ratios)

    scale_ratio = ratios.min()
    sqlshare_scaled = scale_ratio * counts_sqlshare
    print("SQLShare Scaled:")
    print(sqlshare_scaled)
    print("SQLyzr Counts:")
    print(counts_sqlyzr)
    print("SQLShare Counts:")
    print(counts_sqlshare)

    sqlyzr_questions = sqlyzr_uniq_questions(in_file)

    stat_rows = dict()
    for index, row in sqlyzr_questions.iterrows():
        idx = row['ds_idx']
        spider_row = spider_dict[int(idx.replace("spider", ""))]
        db_id = spider_row['db_id']
        stat_rows.setdefault(db_id, []).append(row)

    stat_rows_sorted = sorted(stat_rows.items(), key=lambda x: len(x[1]), reverse=True)

    stat_rows_sorted = list(filter(lambda x: x[0] not in skip_dbs, stat_rows_sorted))

    cats = sqlshare_scaled.index.tolist()
    aligned_rows = {c: set() for c in cats}
    aligned_db_ids = set()
    for db_id, stat_rows in stat_rows_sorted:
        if db_id in skip_dbs or db_id not in scale_dbs:
            continue
        for row in stat_rows:
            cat = row['cat']
            idx = row['ds_idx']
            spider_row = spider_dict[int(idx.replace("spider", ""))]
            spider_row_db_id = spider_row['db_id']
            if len(aligned_rows[cat]) < sqlshare_scaled[cat]:
                aligned_rows[cat].add(str(row['ds_idx']))
                aligned_db_ids.add(spider_row_db_id)
                aligned_db_ids.add(db_id)

    for cat, rows in aligned_rows.items():
        print(cat, len(rows))

    aligned_ids = set().union(*aligned_rows.values())
    print(len(aligned_ids))

    df['ds_idx'] = df['dst'].astype(str) + df['ds_idx'].astype(str)

    db_ids = set()
    aligned_rows = []
    orig_data = []
    for index, row in df.iterrows():
        cat = row['cat']
        idx = row['ds_idx']
        spider_row = spider_dict[int(idx.replace("spider", ""))]
        db_id = spider_row['db_id']
        if row['ds_idx'] in aligned_ids:
            aligned_rows.append(row)
            db_ids.add(db_id)
            orig_data.append(spider_row)

    # print(aligned_db_ids)
    print(len(db_ids))
    print(db_ids)
    #
    print(len(aligned_rows))
    aligned_df = pd.DataFrame.from_records(aligned_rows)
    aligned_df.to_csv(out_file)

    assert set(db_ids).issubset(set(scale_dbs))

    json_path = out_file.replace(".csv", ".json")
    write_json(json_path, orig_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-s", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.s, args.o)
