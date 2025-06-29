import re

import matplotlib.pyplot as plt
import pandas as pd
import tqdm
import seaborn as sns

from src.cat.tag_extractor import TagExtractor
from src.parse.lexer import get_lexer
from src.parse.parser import SqlParser
from src.util.log_util import configure_logging
from src.util.str_utils import shrink_whitespaces
from src.cat.catter import Catter
from natsort import natsorted

configure_logging()

data_dir = 'data/sqlshare_data_release/'

df = pd.read_csv(data_dir + "cats.csv")
print(len(df))

df = df[df['cat'] != 'c1000']

parser = SqlParser()
tag_extractor = TagExtractor()

# for i, row in df.iterrows():
#     sql = row['sql']
#     ast = parser.parse(sql)
#     tags = tag_extractor.extract_tags(ast)
#     print(tags)
#
#
# print(len(df))

stat = df.drop(columns=['sql', 'sub']).groupby(['cat'])
percentages = df['cat'].value_counts(normalize=True).sort_index() * 100
print(percentages)

plt.figure(figsize=(5, 5))
cats = natsorted(df['cat'].unique())
sns.countplot(df, x="cat", order=cats)

plt.savefig(f"catcount.png", bbox_inches='tight', dpi=300)
plt.show()
