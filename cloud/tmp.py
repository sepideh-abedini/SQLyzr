import pandas as pd

from src.rel.sql_data import SqlParsedData
from src.rel.sql_transformer import AddLimitTransformer

# df = pd.read_csv("charts/all_scores_new_v7.csv")
#
# df = df[df['cat'].isna()]
#
# print(len(df))
#
gold = "SELECT * FROM BAR LIMIT 10"
pred = "SELECT * FROM BAR LIMIT 7"

t = AddLimitTransformer()

p = SqlParsedData("id", pred, None)
g = SqlParsedData("id", gold, None)

new_pred, new_gold = t.transform_sql(p, g)
print(new_pred.sql)
