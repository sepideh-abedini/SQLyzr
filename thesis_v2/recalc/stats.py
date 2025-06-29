import pandas as pd

df = pd.read_csv("rea_new.csv")
print(df[['model', 'ea']].groupby('model').mean())
print(df[['model', 'rea']].groupby('model').mean())

df = pd.read_csv("thesis_scores_v2.csv")
print(df[['model', 'ea']].groupby('model').mean())
print(df[['model', 'rea']].groupby('model').mean())
