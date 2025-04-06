import pandas as pd
import tqdm
from natsort import natsorted

from scripts.chart_lib.drawer import Drawer, proc_df

# SCORES_PATH = "charts/all_scores_v1.csv"
SCORES_PATH = "charts/all_scores_new_v3.csv"

drawer = Drawer(SCORES_PATH)
metrics = [
    "Execution Accuracy",
    "Relaxed Execution Accuracy",
    "Exact Match",
    "Execution Time",
    "Execution Time Consistency",
    "Token Usage",
    "Complexity Consistency",
    # "REA-EA Diff"
]

# drawer.draw_overall()
# for metric in tqdm.tqdm(metrics):
#     drawer.draw(metric)
drawer.draw_cats()

exit(0)

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
