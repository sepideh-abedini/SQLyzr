import pandas as pd

from src.util.file_utils import read_json

ds = "spider"
df = pd.read_csv("thesis_scores.csv")
df = df[df['dst'] == ds]

pred_cats = read_json("pred_data/pred_cats.json")

new_rows = []
for index, row in df.iterrows():
    row_dict = row.to_dict()
    idx = row_dict['ds_idx']

    pred_cats_row = pred_cats[idx]
    row_dict['pcat'] = pred_cats_row['pcat']
    row_dict['psub'] = pred_cats_row['psub']
    new_rows.append(row_dict)

new_df = pd.DataFrame(new_rows)
new_df.to_csv("thesis_v2/catted.csv")
