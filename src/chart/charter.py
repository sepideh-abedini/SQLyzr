import os
import shutil
from typing import List

import pandas as pd
import tqdm
from dataclasses_json.stringcase import snakecase
from natsort import natsorted

from scripts.chart_lib.drawer import Drawer
from src.sqlyzr.chart_config import ChartName


# SCORES_PATH = "charts/all_scores_v1.csv"
# SCORES_PATH = "charts/all_scores_new_v7.csv"
# drawer = Drawer(SCORES_PATH, include_all=True, show=True)
# drawer.draw("Execution Accuracy")


# exit(0)


def draw_all_charts(scores_path: str, out_dir: str, included_charts: List[ChartName], hue):
    # if os.path.exists(out_dir):
    #     shutil.rmtree(out_dir)
    #     os.mkdir(out_dir)

    drawer = Drawer(scores_path, show=False, out_dir=out_dir, hue=hue)
    if "Category Distribution" in included_charts:
        drawer.draw_cats()
    if "Overall" in included_charts:
        drawer.draw_overall()
    if "Gold Execution Time Scaled" in included_charts:
        drawer.draw_exec_time_scale()

    drawer = Drawer(scores_path, include_all=True, show=False, out_dir=out_dir, hue=hue)
    metrics = [
        "Execution Accuracy",
        "Relaxed Execution Accuracy",
        "Exact Match",
        "Execution Time",
        "Token Usage",
    ]
    for metric in tqdm.tqdm(metrics):
        if metric in included_charts:
            drawer.draw(metric)

    drawer = Drawer(scores_path, include_all=True, show=False, only_correct=True, out_dir=out_dir, hue=hue)
    metrics = [
        "Execution Time Consistency",
        "Execution Time Inconsistency",
    ]
    for metric in tqdm.tqdm(metrics):
        if metric in included_charts:
            drawer.draw(metric)

    drawer = Drawer(scores_path, include_all=True, only_correct=True, show=False, exclude_c6=True, out_dir=out_dir, hue=hue)
    metrics = [
        "Complexity Consistency",
        "Complexity Inconsistency"
    ]
    for metric in tqdm.tqdm(metrics):
        if metric in included_charts:
            drawer.draw(metric)


# draw_all_charts("charts/all_scores_v8.csv")


def first_letters(s):
    s = s.lower()
    return "".join(map(lambda w: w[0], s.split(" ")))


def copy_charts():
    os.makedirs("charts/paper", exist_ok=True)

    shutil.copy("charts/cat_count.png", f"charts/paper/catcount.png")
    shutil.copy("charts/sub_cat_count.png", f"charts/paper/subcount.png")
    shutil.copy("charts/overall.png", f"charts/paper/overall.png")

    metrics = [
        "Execution Accuracy",
        "Relaxed Execution Accuracy",
        "Exact Match",
        "Execution Time",
        "Token Usage",
        "Execution Time Consistency",
        "Execution Time Inconsistency",
        "Complexity Consistency",
        "Complexity Inconsistency"
    ]
    for m in metrics:
        p = f"charts/{snakecase(m)}/mean__{snakecase(m)}_per__category.png"
        shutil.copy(p, f"charts/paper/{first_letters(m)}cat.png")

    for m in metrics:
        p = f"charts/{snakecase(m)}/mean__{snakecase(m)}_per__sub_category.png"
        shutil.copy(p, f"charts/paper/{first_letters(m)}sub.png")


# draw_all_charts()
# copy_charts()
# exit(0)

model = "dail"


def means(model):
    df = proc_df(SCORES_PATH)
    df = df[df['Model'] == model]
    df = df[["SubCategory", "Relaxed Execution Accuracy"]]
    df = df.groupby("SubCategory").mean().sort_values("Relaxed Execution Accuracy", ascending=False)
    df = df.reset_index()
    return df['SubCategory']


def counts():
    df = proc_df(SCORES_PATH)
    df = df[df['Model'] == "din"]
    df = df[["SubCategory"]]
    df = df.groupby("SubCategory").size()
    df = df.reset_index(name="count")
    sub_cats = natsorted(df['SubCategory'].unique())
    df['SubCategory'] = pd.Categorical(df['SubCategory'], categories=sub_cats, ordered=True)
    df = df.sort_values(by="SubCategory")
    return df


# print(df)
# plt.figure(figsize=(30, 5))
# for i in range(0, 35):
#     if f"s{i}" not in df['SubCategory'].unique():
#         print(f"s{i} not in df['SubCategory'].unique()")

# ax = sns.countplot(df, x="SubCategory", order=[f"s{i}" for i in range(0, 35)], hue="Model")
# plt.show()

def longest_common_subsequence(s1: str, s2: str) -> str:
    m, n = len(s1), len(s2)

    # Create a 2D dp array where dp[i][j] stores the length of LCS of s1[:i] and s2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Build the dp table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Recover the LCS from the table
    i, j = m, n
    lcs = []

    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:  # Match found, move diagonally up
            lcs.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:  # Move to the larger value
            i -= 1
        else:
            j -= 1

    # LCS is constructed in reverse order, so reverse it
    return list(reversed(lcs))

# df = counts()
# print(df)
# plt.figure(figsize=(20, 5))
# sns.barplot(df, x="SubCategory", y="count")
# plt.show()
# print(counts())
# Example Usage
# s1 = list("ABAZDC")
# s2 = list("BACBAD")
# s1 = list(bar("din"))
# s2 = list(bar("dail"))
# result = longest_common_subsequence(s1, s2)
# print("The longest common subsequence is:", result)
