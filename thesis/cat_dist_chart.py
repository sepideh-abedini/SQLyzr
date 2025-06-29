import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import os
from natsort import natsorted


def draw_cats():
    # df = pd.read_csv("thesis_scores.csv")
    df = pd.read_csv("align/sqlshare_cats.csv")
    # df = df[(df['tmp'] == 0.2) & (df['itr'] == 0) & (df['model'] == 'din')]
    df = df[df['cat'] != "c1000"]
    print(df.groupby('cat')['cat'].value_counts())
    print(df['sub'].value_counts())
    print(df['sub'].value_counts().sum())
    print(df['sub'].value_counts(normalize=True))
    print(df['sub'].value_counts(normalize=True).sum())
    print(len(df))
    plt.figure(figsize=(5, 5))
    sns.countplot(data=df, x="cat", order=natsorted(df["cat"].unique()))
    plt.show()


draw_cats()
