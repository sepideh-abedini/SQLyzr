import pandas as pd

df = pd.read_csv("charts/all_scores_new_v7.csv")

COLS = {
    'sub_cat': 'sub',
    'cc': 'plc',
    'dataset': 'dst'
}

df = df.rename(columns=COLS)
df['plt'] = df.apply(lambda e: int((e['et'] / e['get']) > 1.1), axis=1)
df['pcat'] = 'c1'
df['psub'] = 's1'

df.to_csv("charts/all_scores_v8.csv")
