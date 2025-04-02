import pandas as pd

dirr = "data/dail_spider_all"
df = pd.read_csv(f"{dirr}/scores_raw.csv")
tokdf = pd.read_csv(f"{dirr}/eval/scores_toks.csv")
print(len(df))
print(len(tokdf))

# if "get" in ccdf:
df['tokens'] = tokdf['tokens']
# if "cc" in ccdf:
#     df['cc'] = ccdf['cc']
# print(len(df))
# # df = df.merge(ccdf)
df.to_csv(f"{dirr}/scores_raw_with_toks.csv")
