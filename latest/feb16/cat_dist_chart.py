import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import os
from natsort import natsorted


def draw_cats():
    df = pd.read_csv("sqlshare_c1_s4.csv")
    # df = pd.read_csv("sqlyzr_c1_s4_aligned.csv")
    df = df[df['cat'] != "c1000"]
    # df = df[(df['tmp'] == 0.2) & (df['model'] == "din") & (df['itr'] == 0)]
    df.loc[df['sub'] == 's34', 'cat'] = 'c4'
    # df.loc[df['sub'] == 's31', 'cat'] = 'c6'

    c4 = df[df['cat'] == 'c4']
    c5 = df[df['cat'] == 'c5']
    c6 = df[df['cat'] == 'c6']
    print(len(c4))
    print(len(c5))
    print(len(c6))
    print(c5.groupby(["sub"])["sub"].value_counts())
    print(c6.groupby(["sub"])["sub"].value_counts())

    plt.figure(figsize=(5, 5))

    # print(print(df["cat"].value_counts(normalize=False)))
    # print(print(df["cat"].value_counts(normalize=True)))

    sns.countplot(data=df, x="cat", order=natsorted(df["cat"].unique()))
    plt.savefig(os.path.join(f"cat_count.png"))
    plt.show()

    # plt.figure(figsize=(50, 5))
    # sns.countplot(df, x="SubCategory")
    # plt.savefig(os.path.join(f"sub_cat_count.png"))


draw_cats()
