import pandas as pd

from src.cat.categorizer import Categorizer
from src.cat.catter import Catter
from src.cat.tag_collector import TagCollector
from src.cat.tag_extractor import TagExtractor
from src.chart.drawer import Drawer
from src.parse.graph_drawer import draw_graph
from src.parse.parser import SqlParser
from src.rel.sql_data import SqlParsedData

# from src.rel.sql_transformer import AddLimitTransformer

# df = pd.read_csv("charts/all_scores_new_v7.csv")
#
# df = df[df['cat'].isna()]
#
# print(len(df))
#
# gold = "SELECT * FROM BAR LIMIT 10"
# pred = "SELECT * FROM BAR LIMIT 7"
#
# t = AddLimitTransformer()
#
# p = SqlParsedData("id", pred, None)
# g = SqlParsedData("id", gold, None)
#
# new_pred, new_gold = t.transform_sql(p, g)
# print(new_pred.sql)
sql = "SELECT name, age FROM students WHERE age > 18 AND grade = 'A'"

parser = SqlParser()

ast = parser.parse(sql)

col = TagCollector()

catter = Catter()

te = TagExtractor()

tags = te.extract_tags(ast)

catter.get_sub_category(sql)
print(tags.tag_set.tags)

draw_graph(ast, "/tmp/tmp.png")

# print(tags)

# print(tags)

# col = TagCollector()
