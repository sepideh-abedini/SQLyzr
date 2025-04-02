import pandas as pd

dirr = "data/dail_spider_all"
df = pd.read_csv(f"{dirr}/eval_all/scores_raw.csv")
# df = pd.read_csv(f"{dirr}/scores_raw.csv")
ccdf = pd.read_csv(f"{dirr}/eval/scores_raw.csv")
print(len(df))
print(len(ccdf))

if "get" in ccdf:
    df['get'] = ccdf['get']
if "cc" in ccdf:
    df['cc'] = ccdf['cc']
print(len(df))
# df = df.merge(ccdf)
df.to_csv(f"{dirr}/scores_raw.csv")
