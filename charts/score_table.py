import pandas as pd

from src.eval.lib import confidence_level_interval

df = pd.read_csv("charts/all_scores_new_v3.csv")

df = df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")])
df = df.drop(columns=["ds_idx"])
df['count'] = 1

print(df.columns)

aggs = dict()

metric_names = ["em", "ea", "rea", "et", "cc", "tokens", "count"]

for m in metric_names:
    aggs[f"{m}_sum"] = pd.NamedAgg(column=m, aggfunc='sum')
    aggs[f"{m}_mean"] = pd.NamedAgg(column=m, aggfunc='mean')
    aggs[f"{m}_ci"] = pd.NamedAgg(column=m, aggfunc=confidence_level_interval)
df_cat_subcat = df.groupby(['tmp', 'cat', "sub_cat", "model"]).agg(
    **aggs
)
df_cat_subcat = df_cat_subcat.reset_index()
# df_cat_subcat.to_csv(config.get_scores_path("_cat_subcat"))
#
df_cat = df.groupby(['tmp', 'cat', 'model']).agg(
    **aggs
)
df_cat['sub_cat'] = 'all'
df_cat = df_cat.reset_index()
# df_cat.to_csv(config.get_scores_path("_cat"))
#
df_all = df.groupby(['tmp', "model"]).agg(
    **aggs
)
df_all = df_all.reset_index()
df_all['sub_cat'] = 'all'
df_all['cat'] = 'all'
# df_all = df_all.reset_index()
# df_all.to_csv(config.get_scores_path("_all"))
#
combined = pd.concat([df_cat_subcat, df_cat, df_all], ignore_index=True)
# combined.to_csv(config.get_scores_path("_combined"))
#
# #
final = combined.copy()
final = final.round(2)
final.to_csv("charts/table.csv")
