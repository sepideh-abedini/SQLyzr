import pandas as pd
import tqdm

from src.cat.catter import Catter
from src.util.file_utils import read_json

df = pd.read_csv("charts/all_scores_with_id_v2.csv")

bird = read_json("charts/bird.json")
spider = read_json("charts/spider.json")
beaver = read_json("charts/beaver.json")

datasets = {
    "bird": bird,
    "spider": spider,
    "beaver": beaver
}

catter = Catter()

# cat = catter.get_category(datasets['spider'][3932]['query'])
# subcat = catter.get_sub_category(datasets['spider'][3932]['query'])
# print(cat)
# print(subcat)
# exit(0)

rows = []
c = 0
sc = 0
for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
    orig_cat = row['cat']
    orig_sub_cat = row['sub_cat']
    idx = row['ds_idx']
    ds = row['dataset']
    dataset = datasets[ds]
    sql = dataset[idx]['query']
    cat = catter.get_category(sql)
    sub_cat = catter.get_sub_category(sql)
    row['sub_cat'] = sub_cat
    rows.append(row)
    if cat.name != orig_cat:
        c += 1
        print("HEREEE", orig_cat)
    if sub_cat.name != orig_sub_cat:
        sc += 1
        # print(f"DIFF: {orig_cat}:{orig_sub_cat} -> {cat}:{sub_cat}")

new_df = pd.DataFrame(rows)
new_df.to_csv("charts/all_scores_new_v6.csv")
print(c)
