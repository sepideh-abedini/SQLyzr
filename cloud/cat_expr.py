import pandas as pd
import tqdm
from natsort import natsorted

from src.cat.catter import Catter
from src.cat.tag_extractor import TagExtractor
from src.cat.tags.expr_type import ExprType
from src.cat.tags.extra import ExtraKeywords
from src.cat.tags.group_cond import GroupType
from src.cat.tags.join_cond import JoinConditions
from src.cat.tags.join_type import JoinSub, JoinType
from src.parse.graph_drawer import draw_graph
from src.parse.parser import SqlParser
from src.util.file_utils import read_json

data = read_json("charts/in.json")

counts = {}


# parser = SqlParser()
# sql = "SELECT CAST(SUM(type = 'gold' AND STRFTIME('%Y', issued) < '1998') AS REAL) * 100 / COUNT(card_id) FROM card"
# sql = "Select a * 2 from b"
# ast = parser.parse(sql)
# draw_graph(ast, "bar.png")

# exit(0)


def cts():
    catter = Catter()
    tag_extractor = TagExtractor()
    parser = SqlParser()
    for row in tqdm.tqdm(data):
        sql = row['query']
        ast = parser.parse(sql)
        sub = catter.get_sub_category(sql)
        counts[sub.name] = counts.setdefault(sub.name, 0) + 1
        # if sub.name == "s0":
        #     print(sql)
        #     tags = tag_extractor.extract_tags(ast)
        #     print(tags.tag_set.tags)
    print("done")


cts()
df = pd.DataFrame(counts.items())
df.to_csv("cats.count.csv")

# print(counts)
exit(0)


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
def export_joins():
    catter = Catter()
    tag_extractor = TagExtractor()
    parser = SqlParser()
    # c = 0
    newd = []
    all_tags = set()
    counts = dict()
    for row in tqdm.tqdm(data):
        sql = row['query']
        ast = parser.parse(sql)
        tags = tag_extractor.extract_tags(ast)
        sub = catter.get_sub_category(sql)
        counts[sub.name] = counts.setdefault(sub.name, 0) + 1
        if sub.name.lower() == "s22":
            tag_names = set(map(str, tags.tag_set.tags))
            stat = {item: 1 for item in tag_names}
            newd.append(stat)
    df = pd.DataFrame(newd)
    print(len(df))
    df.to_csv("joins.csv")


# export_joins()
# exit(0)
df = pd.read_csv("joins.csv")
print(len(df))

subs1 = {
    "s25_4_4_5": {JoinSub.INNER, JoinConditions.ConditionalJoin, ExtraKeywords.AGGREGATE},
    "s25_4_4_4": {JoinSub.INNER, JoinConditions.ConditionalJoin, ExprType.ArithExpr},
    "s25_4_4_3": {JoinSub.INNER, JoinConditions.ConditionalJoin, GroupType.ConditionalGroup},
    "s25_4_4_2": {JoinSub.INNER, JoinConditions.ConditionalJoin, GroupType.UnconditionalGroup},
    "s25_4_4_1": {JoinSub.INNER, JoinConditions.ConditionalJoin, ExtraKeywords.OrderBy},
    "s25_4_3": {JoinSub.INNER, JoinType.EquiJoin},
    "s25_4_2": {JoinSub.INNER, JoinType.NonEquiJoin},
    "s25_4_1": {JoinSub.INNER, JoinConditions.UnconditionalJoin},
    "s25_3": {JoinSub.LEFT},
    "s25_2": {JoinSub.RIGHT},
    "s25_1": {JoinSub.OUTER},
}

subs2 = {
    "s25_5": {JoinType.NonSimpleJoin, ExtraKeywords.AGGREGATE},
    "s25_4": {JoinType.NonSimpleJoin, GroupType.UnconditionalGroup},
    "s25_3": {JoinType.NonSimpleJoin, ExtraKeywords.OrderBy},
    "s25_2": {JoinType.NonSimpleJoin, JoinType.EquiJoin},
    "s25_1": {JoinType.NonSimpleJoin, JoinSub.INNER},
}

sub_count = {}


def has_tag(row, tags):
    for t in tags:
        if row[t.name] != 1:
            return False
    return True


s251_rows = []

for i, row in df.iterrows():
    all_tags = natsorted(subs2.items(), key=lambda x: x[0], reverse=True)
    for sub, tags in all_tags:
        if has_tag(row, tags):
            sub_count[sub] = sub_count.setdefault(sub, 0) + 1
            if sub == "s25_1":
                s251_rows.append(row)
            break
# print(len(s251_rows))
# data = pd.DataFrame(s251_rows)
# print(data.sum())
# data.to_csv("final.csv")
#
print(len(df))
print(sub_count)
print(sum(sub_count.values()))
