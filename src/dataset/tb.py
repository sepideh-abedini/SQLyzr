from src.configs.datasets import BEAVER_DEV, BEAVER_SMALL
from src.eval.exact_match import ExactMatchParser
from src.eval.lib import DatabaseClient
from src.parse.parser import SqlParser
from src.util.file_utils import read_json


def main():
    data = read_json(BEAVER_DEV.get_rel_path("non_dw.dev.conv.small.json"))
    dbc = DatabaseClient(BEAVER_DEV)
    c = 0
    for entry in data:
        db_id = entry['db_id']
        sql = entry['sql']
        res = dbc.exec_mysql(db_id, sql)
        parser = SqlParser()
        tables_path = BEAVER_SMALL.get_tables_path()
        parser = ExactMatchParser(tables_path)
        ast = parser.parse(sql, db_id)
        if res is None:
            c += 1
        if ast is None:
            c += 1
            # print(f"db_id = {db_id}")
            # print(sql)
    print(c)


if __name__ == '__main__':
    main()
