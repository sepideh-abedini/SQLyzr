import pandas as pd

SCORES_PATH = "all_scores_v1.csv"

sub_to_cat = {
    's0':'c1',
    's1': 'c1',
    's2': 'c1',
    's3': 'c2',
    's4': 'c2',
    's5': 'c2',
    's6': 'c2',
    's7': 'c2',
    's8': 'c2',
    's9': 'c2',
    's11': 'c3',
    's10': 'c3',
    's13': 'c3',
    's12': 'c3',
    's14': 'c3',
    's15': 'c3',
    's16': 'c3',
    's17': 'c3',
    's18': 'c3',
    's19': 'c3',
    's20': 'c4',
    's21': 'c4',
    's22': 'c4',
    's23': 'c4',
    's24': 'c4',
    's25': 'c4',
    's26': 'c5',
    's27': 'c5',
    's28': 'c5',
    's29': 'c5',
    's30': 'c6',
    's31': 'c6',
    's32': 'c6',
    's33': 'c6',
    's34': 'c6'
}

df = pd.read_csv(SCORES_PATH)
df['cat'] = df['sub_cat'].map(lambda x: sub_to_cat[x] if x in sub_to_cat else None)
# df['sub_cat'] = df['sub_cat'].map(lambda x: sub_to_cat[x]['sub_cat'] if x in sub_to_cat else None)
# data_dict.get(df['sub_cat'])
# df[['cat', 'sub_cat']] = df['sub_cat'].apply(
#     lambda x: pd.Series(data_dict[df['sub_cat']]))
# print(df.count())
# print(df['sub_cat'].count())
# print(nan_count)
df.to_csv("all_scores_v3.csv")
