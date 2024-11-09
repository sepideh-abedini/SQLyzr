from itertools import count

from src.sql_parser.parser import SqlParser
from utils import parse


def parse_all():
    parser = SqlParser()

    path = "data/dataset/bird/"
    errors = []

    with open(path + "train_gold.sql", 'r') as f:
        total = 0
        count = 0
        for line in f:
            total += 1
            try:
                sql, db_id = line.split("\t")
                p = parser.parse(sql)
            except SyntaxError as e:
                errors.append(line)
                count += 1
                print(f"____error_{count}______:", sql)
        print(f"{count}/{total}")


def parse_single():
    parser = SqlParser()
    line = "SELECT teacher_ny_teaching_fellow end FROM projects WHERE teacher_acctid = '42d43fa6f37314365d08692e08680973'"
    p = parser.parse(line)
    # print(p)


def main():
    parse_all()
    # parse_single()


if __name__ == '__main__':
    main()
#
# with open(path + "errors.txt", 'w') as f:
#     for error in errors:
#         f.write(f"{error}")
