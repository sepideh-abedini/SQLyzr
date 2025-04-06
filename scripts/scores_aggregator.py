import os.path

import pandas as pd

DATA_DIRS = [
    "dail_spider_all",
    "dail_bird_all",
    "dail_beaver_all",
    "din_spider_all",
    "din_bird_all",
    "din_beaver_all"
]


def parse_data_dir(data_dir: str):
    [model, dataset, size] = data_dir.split("_")
    return model, dataset, size


dfs = []
for data_dir in DATA_DIRS:
    model, dataset, size = parse_data_dir(data_dir)
    raw_scores_path = os.path.join("data", data_dir, "scores_raw_with_toks.csv.new.csv")
    df = pd.read_csv(raw_scores_path)
    print(df.columns)
    df['model'] = model
    df['dataset'] = dataset
    df = df.add_prefix(f"{model}_{dataset}_", axis=0)
    dfs.append(df)

agg_df = pd.concat(dfs)

agg_df.to_csv(os.path.join("data", "all.csv"))

# sample = agg_df.groupby(["tmp", "dataset", "model"]).apply(lambda df: df.sample(100))
# sample.to_csv(os.path.join("data", "sample.csv"))

# catter = Catter()
# rows = []
# for dataset in ["spider", "bird", "beaver"]:
#     with open(f"charts/data/{dataset}.sql") as file:
#         lines = file.readlines()
#         for line in tqdm.tqdm(lines, total=len(lines), desc=dataset):
#             sql = line.split("\t")[0]
#             cat = catter.get_category(sql)
#             rows.append({"dataset": dataset, "cat": cat.name if cat else None, "count": 1})
# df = pd.DataFrame(rows)
# df.to_csv(os.path.join("data", "cats.csv"))
