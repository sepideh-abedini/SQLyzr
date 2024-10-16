from itertools import count

from fontTools.misc.psOperators import ps_real

from src.sql_parser.parser import SqlParser
from utils import parse

parser = SqlParser()

path = "data/datasets/bird/"
errors = []

with open(path + "gold.txt", 'r') as f:
    total = 0
    count = 0
    for line in f:
        total += 1
        try:
            p = parser.parse(line)
        except SyntaxError as e:
            errors.append(line)
            count += 1
            print(f"____error_{count}______:", line)
    print(f"{count}/{total}")
#
# with open(path + "errors.txt", 'w') as f:
#     for error in errors:
#         f.write(f"{error}")





