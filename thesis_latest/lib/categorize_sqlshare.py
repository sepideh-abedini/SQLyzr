import argparse

import pandas as pd
import tqdm

from src.cat.catter import Catter
from src.parse.parser import SqlParser
from src.util.log_util import configure_logging

configure_logging()



def main(in_file, out_file):
    with open(in_file, 'r') as f:
        content = f.read()

    sqls = content.split("\n")

    parser = SqlParser()
    catter = Catter()
    c = 0

    rows = []
    with open("errors.txt", 'w') as f:
        for sql in tqdm.tqdm(sqls, total=len(sqls)):
            ast = parser.parse(sql)
            cat, sub = catter.categorize(sql)
            rows.append({
                'sql': sql,
                'cat': cat.name,
                'sub': sub.name
            })
            if not ast:
                c += 1
                f.write(sql + "\n")
        print(c)
        print(len(sqls))

    df = pd.DataFrame(rows)
    df.to_csv(out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
