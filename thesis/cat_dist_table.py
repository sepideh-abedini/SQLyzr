import pandas as pd
from natsort import natsorted

sqlyzr = pd.read_csv("thesis_scores.csv")
sqlyzr = sqlyzr[(sqlyzr['tmp'] == 0.2) & (sqlyzr['itr'] == 0) & (sqlyzr['model'] == 'din')]
aligned = pd.read_csv("thesis_aligned_100.csv")
aligned = aligned[(aligned['tmp'] == 0.2) & (aligned['itr'] == 0) & (aligned['model'] == 'din')]
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
