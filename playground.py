from src.cat.catter import Catter
from src.parse.graph_drawer import draw_graph
from src.parse.parser import SqlParser

catter = Catter()

sql = "SELECT T1.`School Name`, T2.Street, T2.City, T2.State, T2.Zip FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Monterey' AND T1.`Free Meal Count (Ages 5-17)` > 800 AND T1.`School Type` = 'High Schools (Public)'"
sql = "SELECT T2.School, T1.AvgScrWrite, T2.Phone FROM schools AS T2 LEFT JOIN satscores AS T1 ON T2.CDSCode = T1.cds WHERE strftime('%Y', T2.OpenDate) > '1991' OR strftime('%Y', T2.ClosedDate) < '2000'"
sql = "SELECT x FROM schools WHERE strftime('%Y', T2.OpenDate) > '1991'"
parser = SqlParser()
draw_graph(parser.parse(sql), "graph.png")

cat = catter.get_category(sql)
print(cat)
