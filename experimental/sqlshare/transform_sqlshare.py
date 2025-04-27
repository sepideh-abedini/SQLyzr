import re
from functools import reduce

import sqlglot

import tqdm

from src.parse.parser import SqlParser
from src.util.str_utils import shrink_whitespaces


def convert_top_to_limit(sql):
    # pat = r'.*\btop\b\s+(.*)\s+(.*)'
    pat = r'(.*)\btop\b\s+(\S+)\s+(.*)'
    if re.match(pat, sql, re.IGNORECASE):
        sql = re.sub(pat, r'\1 \3 LIMIT \2', sql, flags=re.IGNORECASE)
    pat2 = r'(.*)\btop\s*\(\s*([^)]+?)\s*\)(.*)'
    if re.match(pat2, sql, re.IGNORECASE):
        sql = re.sub(pat2, r'\1 \3 LIMIT \2', sql, flags=re.IGNORECASE)
    return sql


def find_matching_paren(sql, start_pos):
    depth = 1
    for pos in range(start_pos + 1, len(sql)):
        if sql[pos] == '(':
            depth += 1
        elif sql[pos] == ')':
            depth -= 1
            if depth == 0:
                return pos
    return -1


def replace_substring(s, start, end, replacement):
    return s[:start] + replacement + s[end + 1:]


def fix_sql(sql):
    while re.search(r'\btop\b', sql, flags=re.IGNORECASE):
        match = re.search(r'\((?=[^()]*\btop\b)', sql, flags=re.IGNORECASE)
        if match:
            end = find_matching_paren(sql, match.start())
            sub_sql = sql[match.start() + 1:end]
            sub_sql = shrink_whitespaces(sub_sql)
            sub_sql = convert_top_to_limit(sub_sql)
            sql = replace_substring(sql, match.start() + 1, end - 1, sub_sql)
        else:
            sql = convert_top_to_limit(sql)
    return sql


# put any operators you want inside the character class [+*/-]
TOKEN_SPACES = re.compile(r'\s*([*])\s*')


def normalize_ops(sql: str) -> str:
    """Return expr with exactly one space before/after each + - * / operator."""
    return TOKEN_SPACES.sub(r' \1 ', sql).strip()


def remove_word_comments(sql):
    sql = re.sub(r'--\s*\w+', '', sql)
    return sql


def remove_wait_for(sql):
    sql = re.sub(r'\bWAITFOR\s+DELAY\s+\'[0-9:.]*\'\s*', '', sql, flags=re.IGNORECASE)
    return re.sub(r'\bWAITFOR\b', '', sql, flags=re.IGNORECASE)


def remove_schema_refs(sql):
    pattern = re.compile(
        r'(?:\[[^\]]+\]|\"[^\"]+\"|\w+)\.(\[[^\]]+\]|\"[^\"]+\"|\w+)\.(\[[^\]]+\]|\"[^\"]+\"|\w+)(?!\.)')
    result = re.sub(pattern, r'\1.\2', sql)
    return result


def replace_date_template(sql):
    sql = re.sub(r"\{d\s+'([^']+)'\}", r"'\1'", sql)
    return sql


def fix_double_plus(sql):
    return re.sub(r'\+\s*\+', '+', sql)


err = 0


def transpile(sql):
    global err
    try:
        res = sqlglot.transpile(sql, read="tsql", write="sqlite")[0]
    except Exception as e:
        print(e)
        err += 1
        res = sql
    return res


def split_sql(acc, sql):
    pattern = re.compile(r';\s*(?=select)', flags=re.IGNORECASE)
    matches = list(pattern.finditer(sql))
    positions = [m.start() for m in matches]
    splits = []
    last = 0
    for pos in positions:
        splits.append(sql[last:pos])
        last = pos + 1
    splits.append(sql[last:])
    return acc + splits


# sql = "SELECT x,y FROM (SELECT TOP 1 x,y,ROW_NUMBER() OVER(PARTITION BY x ORDER BY y ASC) AS rownum FROM ( SELECT a.Column1 AS x , b.Column2 AS y FROM [354].[twitter_rv.615784] a JOIN [354].[twitter_rv.615784] b ON a.Column2 = b.Column1 ) joined) joined_distinct OPTION (MERGE JOIN, ORDER GROUP)"
# sql = "SELECT DISTINCT TOP 3 pos,strand FROM [1123].[BiGill_methratio_v9_A.txt] GROUP BY pos, strand"
sql = "SELECT TOP(5) * FROM [1059].[SeaFlow Sfl Data] ORDER BY [time] ASC "
# sql = "SELECT TOP 50 x.fullname, x.c as SiggraphCnt, y.c as AcmTogCnt, x.c+y.c as Total FROM (SELECT a.fullname, count(*) as c FROM [1143].[author] a, [1143].[authored] b, [1143].[inproceedings] p WHERE a.fullname = b.fullname and b.pubID = p.id and p.booktitle='SIGGRAPH' GROUP BY a.fullname) x, (SELECT  a.fullname, count(*) as c FROM [1143].[author] a, [1143].[authored] b, [1143].[article] p WHERE a.fullname = b.fullname and b.pubID = p.id and p.journal='ACM Trans. Graph.' GROUP BY a.fullname LIMIT 10) y WHERE x.fullname = y.fullname ORDER BY Total DESC; "
# sql = "SElECT top 10 * from (SELECT  * FROM [1041].[table_MyTable_dmedv.csv] ORDER BY obj LIMIT 500) qry order by qry.rowc"
# sql = "SELECT Seqname , Source , Feature , StartIdx , EndIdx , Score , Strand , Frame , CASE WHEN CHARINDEX(';', GroupID) = 0 THEN GroupID ELSE SUBSTRING(GroupID, 1, CHARINDEX(';', GroupID)-1) END AS GroupID , CASE WHEN CHARINDEX(';', GroupID) = 0 THEN '' ELSE SUBSTRING(GroupID, CHARINDEX(';', GroupID)+1, LEN(GroupID)) END AS Comment FROM [354].[table_bivalvia_methylated_20CG_20as_20bed.txt.gff]"
# sql = 'SELECT x,y,ROW_NUMBER() OVER(PARTITION BY x ORDER BY y ASC) AS "Row Number" FROM [354].[twitter_join_600k]'
# sql = "SELECT x % 10 AS bucket, SUM(sumdegree) AS edges FROM [354].[twitter_rv.6200000.sumdegree] GROUP BY (x % 10) ORDER BY edges DESC"
# sql = "SELECT  * FROM [823].[CGbigill5x_asgff] WHERE CAST(score AS NUMERIC) < 3 LIMIT 10"
# sql = "SELECT cast(date as char(30)), * FROM [1314howe].[info_escience_senders_detail.txt] where date like '%2011%' order by date desc"
# sql = "select (1) WAITFOR DELAY '00:00:10'"
# sql = "SELECT MIN(latitude), MIN(longitude), MAX(latitude), MAX(longitude) FROM `690`.`All3col` AS maxLat"
sql = transpile(sql)
print(sql)

# sql = "SELECT TOP 5 -- salam baba"
# cleaned_line = re.sub("(.*)--(.*)", r'\1', sql)
# print(cleaned_line)

parser = SqlParser()
ast = parser.parse(sql)
print(ast)
# exit(0)

# sql = normalize_ops(sql)
# print(sql)
# exit(0)

data_dir = 'data/sqlshare_data_release/'
with open(data_dir + "queries_clean.txt", 'r') as f:
    sqls = f.readlines()

sqls = list(reduce(split_sql, sqls, []))
sqls = list(map(lambda sql: shrink_whitespaces(sql), sqls))
sqls = list(map(lambda sql: normalize_ops(sql), tqdm.tqdm(sqls, total=len(sqls))))
sqls = list(map(lambda sql: fix_sql(sql), tqdm.tqdm(sqls, total=len(sqls))))
sqls = list(map(lambda sql: remove_wait_for(sql), tqdm.tqdm(sqls, total=len(sqls))))
sqls = list(map(lambda sql: remove_schema_refs(sql), tqdm.tqdm(sqls, total=len(sqls))))
sqls = list(map(lambda sql: remove_word_comments(sql), tqdm.tqdm(sqls, total=len(sqls))))
sqls = list(map(lambda sql: replace_date_template(sql), tqdm.tqdm(sqls, total=len(sqls))))
sqls = list(map(lambda sql: fix_double_plus(sql), tqdm.tqdm(sqls, total=len(sqls))))
# sqls = list(reduce(lambda acc, sql: acc + [s.strip() for s in sql.split(';') if s.strip()], sqls, []))
# sqls = list(map(lambda sql: transpile(sql), tqdm.tqdm(sqls, total=len(sqls))))
# print("#############################################################")
# print(err)

with open(data_dir + "trs.txt", 'w') as f:
    f.write("\n".join(sqls))
#
# for sql in sqls:
#
#
# print(len(sqls))
