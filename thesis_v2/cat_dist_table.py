import pandas as pd
from natsort import natsorted

sqlyzr = pd.read_csv("thesis_scores.csv")
sqlyzr = sqlyzr[(sqlyzr['tmp'] == 0.2) & (sqlyzr['itr'] == 0) & (sqlyzr['model'] == 'din')]
sqlyzr = sqlyzr[sqlyzr['dst'] == 'spider']
# aligned = pd.read_csv("thesis_aligned_s1.csv")
aligned = pd.read_csv("spider_align/spider_aligned.csv")
aligned = aligned[(aligned['tmp'] == 0.2) & (aligned['itr'] == 0) & (aligned['model'] == 'din')]
# aligned_5 = pd.read_csv("thesis_aligned.csv")
# aligned_5 = aligned_5[(aligned_5['tmp'] == 0.2) & (aligned_5['itr'] == 0) & (aligned_5['model'] == 'din')]
sqlshare = pd.read_csv("align/sqlshare_cats.csv")


def print_cat_dist(df, name):
    df = df[df['cat'] != "c1000"]
    print(f"{name} Count")
    print(df["cat"].value_counts(normalize=False))
    print(f"{name} Percentage")
    print(df["cat"].value_counts(normalize=True))


print_cat_dist(sqlyzr, "sqlyzr")
print_cat_dist(sqlshare, "sqlshare")
print_cat_dist(aligned, "aligned")
# print_cat_dist(aligned_5, "aligned_5")
