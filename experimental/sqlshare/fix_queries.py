import tqdm

from src.cat.tag_extractor import TagExtractor
from src.parse.parser import SqlParser
from src.util.log_util import configure_logging

configure_logging()

data_dir = 'data/sqlshare_data_release/'

with open(data_dir + "errors.txt", 'r') as f:
    sqls = f.readlines()

# sql = "SELECT x-2 FROM bar"
# sql = "SELECT TOP 5 * FROM [354].[Gene_Description_and_Methylation_Ratio_Oyster]"
sql = "SELECT Top 5 * FROM bar"
sql = "SELECT Distinct TABLE_NAME FROM information_schema.TABLES"
sql = "SELECT *, ([M1ratio]+[T1D3ratio]+[T1D5ratio])/3 as mean_chk FROM [1123].[_cast_lineage_1] where [M1ratio]-[mean] <.2"

parser = SqlParser()
# tag_extractor = TagExtractor()
ast = parser.parse(sql)
# print(ast)
# exit(0)

c = 0
for sql in tqdm.tqdm(sqls, total=len(sqls)):
    if "TOP" in sql:
        continue
    ast = parser.parse(sql)
    if not ast:
        c += 1
        print(sql)
print(len(sqls))
print(c)
