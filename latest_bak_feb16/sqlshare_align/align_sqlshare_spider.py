import pandas as pd

from src.cat.catter import Catter
from src.configs.datasets import SPIDER_ALL
from src.util.file_utils import read_json, read_json_to_dict, write_json

skip_dbs = {
    "department_store",
    'baseball_1',
    'store_1',
    'college_2',
    'scientist_1',
    'aan_1',
    'small_bank_1',
    'soccer_2',
    'hospital_1',
    'dorm_1',
    'music_2',
    "flight_1",
    "bakery_1",
    "allergy_1",
    "cre_Doc_Tracking_DB",
    "hr_1",
    "college_1",
    "bike_1"
}

catter = Catter()
spider_data = read_json(SPIDER_ALL.get_test_path())

spider_dict = dict()

for idx, row in enumerate(spider_data):
    row['cat'] = catter.get_category(row['query']).name
    spider_dict[idx] = row


def sqlyzr_uniq_questions(file_path):
    df = pd.read_csv(file_path)
    df = df[df['dst'] == 'spider']
    df['ds_idx'] = df['dst'].astype(str) + df['ds_idx'].astype(str)
    df = df.groupby(['ds_idx'], as_index=False).first()
    return df


def process_sqlyzr(file_path):
    df = pd.read_csv(file_path)
    df = df[df['dst'] == 'spider']
    df['ds_idx'] = df['dst'].astype(str) + df['ds_idx'].astype(str)
    df = df.groupby(['ds_idx'], as_index=False).first()
    df = df[['cat']]
    counts = df['cat'].value_counts().sort_index()
    return counts


def print_cat_dist(cat_file):
    df = pd.read_csv(cat_file)
    df = df[df['cat'] != "c1000"]
    df = df[['cat']]
    counts = df['cat'].value_counts().sort_index()
    return counts


counts_sqlshare = print_cat_dist("latest/sqlshare_align/sqlshare_c1_s4.csv")
counts_sqlyzr = process_sqlyzr("latest/sqlshare_align/sqlyzr_c1_s4.csv")

df = pd.read_csv("latest/sqlshare_align/sqlyzr_c1_s4.csv")
df = df[df['dst'] == 'spider']

print("SQLyzr Total:", df.shape[0])
print("SQLyzr Questions:", counts_sqlyzr.sum())
print("SQLShare Questions:", counts_sqlshare.sum())

ratios = counts_sqlyzr / counts_sqlshare
print("Ratios:")
print(ratios)
# exit(0)

scale_ratio = ratios.min()
sqlshare_scaled = scale_ratio * counts_sqlshare
print("SQLShare Scaled:")
print(sqlshare_scaled)
print("SQLyzr Counts:")
print(counts_sqlyzr)
print("SQLShare Counts:")
print(counts_sqlshare)

sqlyzr_questions = sqlyzr_uniq_questions("latest/sqlshare_align/sqlyzr_c1_s4.csv")

stat_rows = dict()
for index, row in sqlyzr_questions.iterrows():
    cat = row['cat']
    idx = row['ds_idx']
    spider_row = spider_dict[int(idx.replace("spider", ""))]
    db_id = spider_row['db_id']
    stat_rows.setdefault(db_id, []).append(row)

stat_rows_sorted = sorted(stat_rows.items(), key=lambda x: len(x[1]), reverse=True)

for db_id, rows in stat_rows_sorted:
    print(db_id, len(rows))

cats = sqlshare_scaled.index.tolist()
aligned_rows = {c: set() for c in cats}
aligned_db_ids = set()
for db_id, stat_rows in stat_rows_sorted:
    if db_id in skip_dbs:
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
aligned_df.to_csv("latest/sqlshare_align/aligned_spider.csv")

write_json("latest/sqlshare_align/spider_aligned.json", orig_data)
#