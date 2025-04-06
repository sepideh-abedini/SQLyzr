import pandas as pd

SCORES_PATH = "all_scores_v1.csv"

data_dict = {
    's0': {'cat': 'c1', 'sub_cat': 's0'},
    's1': {'cat': 'c1', 'sub_cat': 's1'},
    's2': {'cat': 'c1', 'sub_cat': 's1'},
    's3': {'cat': 'c2', 'sub_cat': 's2'},
    's4': {'cat': 'c2', 'sub_cat': 's3'},
    's5': {'cat': 'c2', 'sub_cat': 's4'},
    's6': {'cat': 'c2', 'sub_cat': 's5'},
    's7': {'cat': 'c2', 'sub_cat': 's6'},
    's8': {'cat': 'c2', 'sub_cat': 's7'},
    's9': {'cat': 'c2', 'sub_cat': 's8'},
    's11': {'cat': 'c3', 'sub_cat': 's9'},
    's10': {'cat': 'c3', 'sub_cat': 's9'},
    's13': {'cat': 'c3', 'sub_cat': 's9'},
    's12': {'cat': 'c3', 'sub_cat': 's10'},
    's14': {'cat': 'c3', 'sub_cat': 's11'},
    's15': {'cat': 'c3', 'sub_cat': 's12'},
    's16': {'cat': 'c3', 'sub_cat': 's13'},
    's17': {'cat': 'c3', 'sub_cat': 's14'},
    's18': {'cat': 'c3', 'sub_cat': 's15'},
    's19': {'cat': 'c3', 'sub_cat': 's16'},
    's20': {'cat': 'c4', 'sub_cat': 's17'},
    's21': {'cat': 'c4', 'sub_cat': 's18'},
    's22': {'cat': 'c4', 'sub_cat': 's19'},
    's23': {'cat': 'c4', 'sub_cat': 's20'},
    's24': {'cat': 'c4', 'sub_cat': 's20'},
    's25': {'cat': 'c4', 'sub_cat': 's21'},
    's26': {'cat': 'c5', 'sub_cat': 's22'},
    's27': {'cat': 'c5', 'sub_cat': 's23'},
    's28': {'cat': 'c5', 'sub_cat': 's24'},
    's29': {'cat': 'c5', 'sub_cat': 's25'},
    's30': {'cat': 'c6', 'sub_cat': 's26'},
    's31': {'cat': 'c6', 'sub_cat': 's27'},
    's32': {'cat': 'c6', 'sub_cat': 's28'},
    's33': {'cat': 'c6', 'sub_cat': 's29'},
    's34': {'cat': 'c6', 'sub_cat': 's30'}
}

df = pd.read_csv(SCORES_PATH)
print(df['sub_cat'].unique())
df['cat'] = df['sub_cat'].map(lambda x: data_dict[x]['cat'] if x in data_dict else None)
df['sub_cat'] = df['sub_cat'].map(lambda x: data_dict[x]['sub_cat'] if x in data_dict else None)
# data_dict.get(df['sub_cat'])
# df[['cat', 'sub_cat']] = df['sub_cat'].apply(
#     lambda x: pd.Series(data_dict[df['sub_cat']]))
# print(df.count())
# print(df['sub_cat'].count())
# print(nan_count)
df.to_csv("all_scores_v2.csv")
