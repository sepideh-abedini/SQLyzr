import pandas as pd
import seaborn as sns
import tqdm
from matplotlib import pyplot as plt
from natsort import natsorted

from src.cat.catter import Catter
from src.chart.charter import draw_all_charts
from src.configs.datasets import DATASETS
from src.eval.lib import confidence_interval
from src.util.file_utils import read_json


def metric_consistency(metric):
    def agg_fun(grouped):
        ea = grouped['ea']
        ms = grouped[metric]
        den = ea.sum()
        if den == 0:
            return 0.0
        return (ea & ms).sum() / den

    return agg_fun


def metric_agg(metric, agg_fun):
    return pd.NamedAgg(column=metric, aggfunc=agg_fun)


METRICS = [
    "em", "ea", "rea", "et", "get", "count"
]

SUMS = {
    f"{m}_sum": pd.NamedAgg(column=m, aggfunc="sum") for m in METRICS
}

MEANS = {
    f"{m}_mean": pd.NamedAgg(column=m, aggfunc="mean") for m in METRICS
}

CIS = {
    f"{m}_ci": pd.NamedAgg(column=m, aggfunc=confidence_interval) for m in METRICS
}


def post_proc(df):
    df = df.drop(columns=['pcat', 'psub', 'dst', 'itr', "id"])
    df['count'] = 1

    sub_grouped = df.groupby(['model', 'tmp', 'cat', 'sub'])
    cc = sub_grouped.apply(metric_consistency('plc'))
    etc = sub_grouped.apply(metric_consistency('plt'))
    sub_grouped = sub_grouped.agg(**SUMS, **MEANS, **CIS)
    sub_grouped['cc'] = cc
    sub_grouped['etc'] = etc
    sub_grouped = sub_grouped.reset_index()

    cat_grouped = df.drop(columns=['sub']).groupby(['model', 'tmp', 'cat'])
    cc = cat_grouped.apply(metric_consistency('plc'))
    etc = cat_grouped.apply(metric_consistency('plt'))
    cat_grouped = cat_grouped.agg(**MEANS, **SUMS, **CIS)
    cat_grouped['cc'] = cc
    cat_grouped['etc'] = etc
    cat_grouped['sub'] = 'all'
    cat_grouped = cat_grouped.reset_index()

    tmp_cat_grouped = df.drop(columns=['sub']).groupby(['model', 'tmp', 'cat'])
    cc = tmp_cat_grouped.apply(metric_consistency('plc'))
    etc = tmp_cat_grouped.apply(metric_consistency('plt'))
    # tmp_cat_grouped = tmp_cat_grouped.mean()
    tmp_cat_grouped_means = tmp_cat_grouped.mean()
    tmp_cat_grouped_means["count"] = tmp_cat_grouped["count"].sum()
    tmp_cat_grouped = tmp_cat_grouped_means
    tmp_cat_grouped['cc'] = cc
    tmp_cat_grouped['etc'] = etc
    tmp_cat_grouped = tmp_cat_grouped.reset_index()

    all_cats = tmp_cat_grouped.drop(columns=['cat']).groupby(['model', 'tmp'])
    all_cats = all_cats.agg(**SUMS, **MEANS, **CIS, cc=pd.NamedAgg(column="cc", aggfunc="mean"),
                            etc=pd.NamedAgg(column="etc", aggfunc="mean"))
    all_cats['cat'] = 'all'
    all_cats['sub'] = 'all'
    all_cats = all_cats.reset_index()

    combined = pd.concat([sub_grouped, cat_grouped, all_cats], ignore_index=True)
    final = combined.copy()
    final = final.round(4)
    final.to_csv("out/scores.csv")


def extract_cats():
    res = []
    for m in ['dail', 'din']:
        for d in ['spider', 'bird', 'beaver']:
            conf = DATASETS[d]['all'][0]
            data = read_json(conf.get_test_path())
            catter = Catter()
            i = 0
            for row in tqdm.tqdm(data, total=len(data)):
                db_id = row['db_id']
                sql = row['query']
                cat = catter.get_category(sql)
                sub = catter.get_sub_category(sql)
                res.append(
                    {'id': f"{m}_{d}_{i}", 'db_id': db_id, 'cat': cat.name, 'sub': sub.name, "sql": sql, "dst": d,
                     "model": m, "itr": 0})
                i += 1
    df = pd.DataFrame(res)
    df.to_csv("out/cats.csv")


def draw(path):
    df = pd.read_csv(path)

    order = natsorted(df['cat'].unique())
    sns.countplot(df, x="cat", order=order)
    plt.savefig("out/cat.png")

    sub_order = natsorted(df['sub'].unique())
    plt.figure(figsize=(50, 5))
    sns.countplot(df, x="sub", order=sub_order)
    plt.savefig("out/sub_count.png")
    sub_order = natsorted(df['sub'].unique())
    sub_order = sub_order + ['all']
    df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col])
    mean_values = df.drop(columns=['sub', "dst", "id", "pcat", "psub"]).groupby(['model', 'cat']).mean()
    mean_values = mean_values.groupby(['model']).mean()
    #
    for value in df['model'].unique():
        new_row = {'model': value, 'cat': "all", "sub": "all"}
        new_row.update(mean_values.loc[value].to_dict())
        row = pd.DataFrame([new_row])
        df = pd.concat([df, row], ignore_index=True)

    df = df.rename(columns={'sub': 'SubCategory', 'rea': "Relaxed Execution Accuracy", 'ea': 'Execution Accuracy',
                            'em': "Exact Match", 'model': "Model"})

    plt.figure(figsize=(50, 5))
    sns.barplot(df, x="SubCategory", hue="Model", y="Relaxed Execution Accuracy", order=sub_order)
    plt.savefig("out/reasub.png")

    plt.figure(figsize=(50, 5))
    sns.barplot(df, x="SubCategory", hue="Model", y="Execution Accuracy", order=sub_order)
    plt.savefig("out/easub.png")

    plt.figure(figsize=(50, 5))
    sns.barplot(df, x="SubCategory", hue="Model", y="Exact Match", order=sub_order)
    plt.savefig("out/emsub.png")


def compare():
    old = pd.read_csv("charts_up/all_scores_v8.csv")
    new = pd.read_csv("out/cats.csv")
    for i, row in tqdm.tqdm(new.iterrows(), total=len(new)):
        oe = old[old['id'] == row['id']].iloc[0]
        if oe['sub'] == 's18':
            print(f"[{row['id']}][{row['cat'], {row['sub']} }]: {row['sql']}")


g = {
    'spider': 9147,
    'bird': 9061,
    'beaver': 185
}


def migrate():
    old = pd.read_csv("out/old/all_scores_v8.csv")
    new = pd.read_csv("out/cats.csv")
    new_rows = []
    for i, row in tqdm.tqdm(old.iterrows(), total=len(old)):
        id = row['id']
        id = int(id.split("_")[2])
        id = id % g[row['dst']]
        ne = new[new['id'] == f"{row['model']}_{row['dst']}_{id}"].iloc[0]
        row['sub'] = ne['sub']
        row['cat'] = ne['cat']
        new_rows.append(row)
        # if i > 100:
        #     break
    new_df = pd.DataFrame(new_rows)
    new_df.to_csv("out/all_scores_v9.csv")


def bar():
    df = pd.read_csv("out/old/all_scores_v8.csv")
    df = df[df['sub'] == "s18"]
    new = pd.read_csv("out/cats.csv")
    catter = Catter()
    for i, row in df.iterrows():
        id = row['id']
        id = int(id.split("_")[2])
        id = id % g[row['dst']]
        ne = new[new['id'] == f"{row['model']}_{row['dst']}_{id}"].iloc[0]
        sql = ne['sql']
        print(row['sub'])
        print(sql)
        print(catter.get_sub_category(sql).name)
    print(len(df))


def tmp():
    df = pd.read_csv("out/all_scores_v9.csv")
    # df =  df[['cat','model','itr','rea']]
    # dtt = df.groupby(["cat", "model"]).mean().reset_index()
    # print(dtt)
    # # print(dtt[dtt['sub'] == 's18'])
    # exit(0)
    cats = pd.read_csv("out/cats.csv")
    # df = pd.read_csv("out/old/all_scores_v8.csv")
    df = df[df['sub'] == "s5"]
    print(len(df))
    for i, row in df.iterrows():
        if row['rea'] == 0:
            id = row['id']
            id = int(id.split("_")[2])
            id = id % g[row['dst']]
            ne = cats[cats['id'] == f"{row['model']}_{row['dst']}_{id}"].iloc[0]
            m = row['model']
            itr = row['itr']
            dst = row['dst']
            with open(f"out/{m}_{dst}_all/pred/pred_0.2_{itr}.txt") as file:
                lines = file.readlines()
                pred = lines[id]
            data = read_json(f"data/{dst}/data.test.json")
            question = data[id]['question']

            print(f"GOLD: {ne['sql']}")
            print(f"PRED: {pred}")
            print(f"NLQ: {question}")
            print(f"Itr: {itr}")
            print(f"Model: {m}")
            print('---------------------------------------------')


def export_scores(path):
    df = pd.read_csv(path)
    post_proc(df)


def main(path):
    # bar()
    # compare()
    # extract_cats()
    # migrate()
    # draw("out/old/all_scores_v8.csv")
    # draw("out/all_scores_v9.csv")
    # bar()
    # tmp()
    # export_scores("out/all_scores_v9.csv")
    draw_all_charts("out/all_scores_v9.csv","out/charts", [
        "Execution Accuracy",
        "Relaxed Execution Accuracy",
        "Exact Match",
        "Execution Time",
        "Token Usage",
        "Execution Time Consistency",
        "Execution Time Inconsistency",
        "Complexity Consistency",
        "Complexity Inconsistency"
    ])


if __name__ == '__main__':
    p = "charts_up/all_scores_v8.csv"
    main(p)
