import pandas as pd
import tqdm

from src.cat.categories import CAT_6, CAT_5, CAT_4, CAT_1, CAT_3
from src.cat.catter import Catter
from src.util.file_utils import read_json

catter = Catter()

data = read_json("data/bird/data.test.json")
# for row in tqdm.tqdm(data):
#     cat, _ = catter.categorize(sql)
#     if cat.name == "c5":
#         print(db_id)
#         print(question)
#         print(sql)
#         print(cat)

df = pd.read_csv("data/dail_bird_all/scores_raw.csv")
df = df[(df['tmp'] == 0.2) & (df['itr'] == 1)]
df = df.reset_index()
# print(len(df))
# print(len(data))
# exit(0)
for i, row in df.iterrows():
    entry = data[i]
    db_id = entry["db_id"]
    sql = entry["query"]
    question = entry["question"]
    if row['rea'] == 0:
        cat, _ = catter.categorize(sql)
        if cat == CAT_4:
            print(i)
            print(db_id)
            print(question)
            print(sql)
# idx =  & (df['rea'] == 0)
# print(idx)
