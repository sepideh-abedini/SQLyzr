import pandas as pd
import tqdm
from natsort import natsorted
from sqlalchemy.testing.suite import JoinTest

from src.cat.catter import Catter
from src.cat.tag_extractor import TagExtractor
from src.cat.tags.expr_type import ExprType
from src.cat.tags.extra import ExtraKeywords
from src.cat.tags.group_cond import GroupType
from src.cat.tags.join_cond import JoinConditions
from src.cat.tags.join_num import NumJoins
from src.cat.tags.join_tables import JoinTables
from src.cat.tags.join_type import JoinSub, JoinType
from src.cat.tags.where_exprs import WhereType
from src.parse.parser import SqlParser
from src.util.file_utils import read_json

data = read_json("charts/in.json")

# df = pd.read_csv("charts/all_scores_v1.csv")
# print(len(df))
# df = df[(df['itr'] == 0) & (df['tmp'] == 0.8) & (df['model'] == 'din')]
# df = df[(df['tmp'] == 0.2) & (df['model'] == 'din')]
# print(len(df))
# print(df.size())
#
# df = df[df['sub_cat'] == 's25']
# print(len(df))
# df = df.groupby(["sub_cat", "itr"]).size()
# df.to_csv("bar.csv")
# print(df)

# df = pd.read_csv("joins.csv")
# print(df.sum())
# exit(0)
#
# catter = Catter()
# tag_extractor = TagExtractor()
# parser = SqlParser()
# c = 0
# newd = []
# all_tags = set()
# counts = dict()
# for row in tqdm.tqdm(data):
#     sql = row['query']
#     ast = parser.parse(sql)
#     tags = tag_extractor.extract_tags(ast)
#     sub = catter.get_sub_category(sql)
#     counts[sub.name] = counts.setdefault(sub.name, 0) + 1
#     if sub.name.lower() == "s25":
#         tag_names = set(map(str, tags.tag_set.tags))
#         stat = {item: 1 for item in tag_names}
#         newd.append(stat)
# df = pd.DataFrame(newd)
# print(len(df))
# df.to_csv("joins.csv")
# exit(0)
#
#
# # print(c)
# #

df = pd.read_csv("joins.csv")

subs1 = {
    "s25_1_1_1": {JoinSub.INNER, JoinConditions.ConditionalJoin, ExtraKeywords.AGGREGATE},
    "s25_1_1_2": {JoinSub.INNER, JoinConditions.ConditionalJoin, ExprType.ArithExpr},
    "s25_1_1_3": {JoinSub.INNER, JoinConditions.ConditionalJoin, GroupType.ConditionalGroup},
    "s25_1_1_4": {JoinSub.INNER, JoinConditions.ConditionalJoin, GroupType.UnconditionalGroup},
    # "s25_1_1_5": {JoinSub.INNER, JoinConditions.ConditionalJoin, JoinTables.MultiJoin},
    "s25_1_1_6": {JoinSub.INNER, JoinConditions.ConditionalJoin, ExtraKeywords.OrderBy},
    "s25_1_2": {JoinSub.INNER, JoinType.EquiJoin},
    "s25_1_3": {JoinSub.INNER, JoinType.NonEquiJoin},
    "s25_1_4": {JoinSub.INNER, JoinConditions.UnconditionalJoin},
    "s25_2": {JoinSub.LEFT},
    "s25_3": {JoinSub.RIGHT},
    "s25_4": {JoinSub.OUTER},
}

subs2 = {
    "s25_1": {WhereType.MultipleWhereExpr},
    "s25_2": {ExtraKeywords.AGGREGATE},
    "s25_3": {ExtraKeywords.OrderBy},
}

sub_count = {}


def has_tag(row, tags):
    for t in tags:
        if row[t.name] != 1:
            return False
    return True


for i, row in df.iterrows():
    all_tags = natsorted(subs1.items(), key=lambda x: x[0], reverse=False)
    for sub, tags in all_tags:
        if has_tag(row, tags):
            sub_count[sub] = sub_count.setdefault(sub, 0) + 1
            break
print(sub_count)
