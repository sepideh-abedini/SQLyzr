import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.eval.lib import confidence_interval

df = pd.read_csv("charts/all_scores_new_v7.csv")

# df = df[df['dataset'] == 'spider']
#
# model = 'din'

# df = df[df['model'] == model]

# df = df.melt(id_vars=['cat', 'model'],
#              value_vars=['em', 'sem'],
#              var_name='metric',
#              value_name='Exact Match')
# df = df.rename(columns={"model": "Model"})
# df["metric"] = df["metric"].replace({"em": "Sqlyzr", "sem": "Spider"})
# df["metric"] = df["metric"].replace({"em": "Sqlyzr", "sem": "Spider"})
#
# ax = sns.barplot(data=df, x='Model', y='Exact Match', hue='metric')
# ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
# ax.set_yticklabels([f'{y:.0%}' for y in ax.get_yticks()])
#
# print(df[['Model', 'metric', 'Exact Match']].groupby(['Model', 'metric']).mean())
#
# plt.savefig(f"charts/paper/eaem.png")
# plt.show()

# df = df[df['model'] == 'din']
# df = df[df['itr'] == 0]
# print(df['sem'].sum())
# print(df['em'].sum())
# print(len(df))

df['count'] = 1
# df = df[['count', 'em', 'sem','cat']]

# df = df.groupby(['cat']).mean()
# print(df)
# print(df['em'].mean())
# print(df['sem'].mean())
# df['diff'] = df['em'] - df['sem']
#
# df = df.round(2)
# df[df.select_dtypes(include='number').columns] *= 100
# df.to_csv("charts/em.csv")


# print(df.columns)

aggs = dict()

metric_names = ["em", "ea", "rea", "et", "cc", "tokens", "count", "sem"]

for m in metric_names:
    aggs[f"{m}_sum"] = pd.NamedAgg(column=m, aggfunc='sum')
    aggs[f"{m}_mean"] = pd.NamedAgg(column=m, aggfunc='mean')
    aggs[f"{m}_ci"] = pd.NamedAgg(column=m, aggfunc=confidence_interval)
df_cat_subcat = df.groupby(['tmp', 'cat', "sub_cat", "model"]).agg(
    **aggs
)
df_cat_subcat = df_cat_subcat.reset_index()

df_cat = df.groupby(['tmp', 'cat', 'model']).agg(
    **aggs
)
df_cat['sub_cat'] = 'all'
df_cat = df_cat.reset_index()

df_all = df.groupby(['tmp', "model"]).agg(
    **aggs
)
df_all['sub_cat'] = 'all'
df_all['cat'] = 'all'
df_all = df_all.reset_index()


combined = pd.concat([df_cat_subcat, df_cat, df_all], ignore_index=True)
final = combined.copy()
final = final.round(4)
final['c'] = final['count_sum'] / 3
final.to_csv("charts/table.csv")
