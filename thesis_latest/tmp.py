import pandas as pd

df1 = pd.read_csv("thesis_latest/data/sqlyzr.csv")
df2 = pd.read_csv("thesis_latest/data/sqlyzr.csv")
df2 = pd.read_csv("file2.csv")

assert (df1['rea'] == df2['rea']).all(), "Columns 'rea' are not exactly equal"
