import pandas as pd

from src.cat.catter import Catter
from src.util.file_utils import read_json, read_json_to_dict, write_json

spider_tables = read_json_to_dict("spider_align/tables.test.json", "db_id")

spider_dict = dict()

THESIS_SCORES_PATH = "thesis_scores_v2.csv"

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
    "bike_1",
    'wine_1',
    'chinook_1',
    'cre_Docs_and_Epenses',
    'e_commerce',
    'cre_Doc_and_collections',
    'cre_Theme_park',
    'planet_1',
    'book_1',
    'cre_Drama_Workshop_Groups',
    'sakila_1',
    'conference',
    'apartment_rentals',
    'student_assessment',
    'video_game',
    'vehicle_driver',
    'medicine_enzyme_interaction',
    'insurance_fnol',
    'sports_competition',
    'flight_4',
    'pilot_1',
    'formula_1',
    'tracking_share_transactions',
    'cre_Doc_Control_Systems',
    'musical',
    'institution_sports',
    'online_exams',
    'cre_Doc_Workflow',
    'program_share',
    'workshop_paper',
    'cinema',
    'swimming',
    'party_host',
    'restaurant_bills',
    'machine_repair',
    'district_spokesman',
    'railway',
    'entertainment_awards',
    'train_station',
    'news_report',
    'browser_web',
    'wedding',
    'sing_contest',
    'school_bus',
    'journal_committee',
    'riding_club',
    'club_leader',
    'local_govt_and_lot',
    "department_management",
    "bike_racing",
    "station_weather",
    "company_employee",
    "performance_attendance",
    "debate",
    "phone_market",
    "local_govt_in_alabama",
    "decoration_competition",
    "solvency_ii",
    "tv_shows"
}

catter = Catter()
spider_data = read_json("spider_align/data.test.json")

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


counts_sqlshare = print_cat_dist("align/sqlshare_cats.csv")
counts_sqlyzr = process_sqlyzr(THESIS_SCORES_PATH)

df = pd.read_csv(THESIS_SCORES_PATH)
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

sqlyzr_questions = sqlyzr_uniq_questions(THESIS_SCORES_PATH)

stat_rows = dict()
for index, row in sqlyzr_questions.iterrows():
    cat = row['cat']
    idx = row['ds_idx']
    spider_row = spider_dict[int(idx.replace("spider", ""))]
    db_id = spider_row['db_id']
    stat_rows.setdefault(db_id, []).append(row)

stat_rows_sorted = sorted(stat_rows.items(), key=lambda x: len(x[1]), reverse=True)

stat_rows_sorted = list(filter(lambda x: x[0] not in skip_dbs, stat_rows_sorted))

for db_id, rows in stat_rows_sorted:
    table = spider_tables[db_id]
    print(db_id, len(rows), len(table['foreign_keys']))

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
# aligned_df = pd.DataFrame.from_records(aligned_rows)
# aligned_df.to_csv("spider_align/spider_aligned.csv")

# write_json("spider_align/spider_aligned.json", orig_data)
#
