import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import os
from natsort import natsorted

from thesis.params import OUT_DIR


def draw_cats():
    # df = pd.read_csv("thesis_scores.csv")
    df = pd.read_csv("align/sqlshare_cats.csv")
    df['Category'] = df['cat']
    # df = df[(df['tmp'] == 0.2) & (df['itr'] == 0) & (df['model'] == 'din')]
    # df = df[df['dst'] == 'spider']
    df = df[df['Category'] != "c1000"]
    print(df.groupby('Category')['Category'].value_counts())
    vc = df['sub'].value_counts()
    print(vc.sum())
    vc = vc.reindex(natsorted(vc.index))
    vc.to_csv("sub_counts.csv")
    print(vc)
    print(df['sub'].value_counts().sum())
    print(df['sub'].value_counts(normalize=True))
    print(df['sub'].value_counts(normalize=True).sum())
    print(len(df))
    plt.figure(figsize=(5, 5))
    sns.countplot(data=df, x="Category", order=natsorted(df["Category"].unique()))
    plt.savefig(f"{OUT_DIR}/sqlshare-dist.png", bbox_inches='tight', dpi=300)
    plt.show()


draw_cats()
