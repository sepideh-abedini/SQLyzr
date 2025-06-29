import argparse

from src.cat.catter import Catter
from thesis_latest.lib.score_lib import process_scores

catter = Catter()

cat_cache = dict()
sub_cache = dict()


def cat_assigner(db_id, pred_sql, gold_sql):
    if gold_sql not in cat_cache:
        cat = catter.get_category(gold_sql)
        cat_cache[gold_sql] = cat.name
    else:
        cat = cat_cache[gold_sql]
    return cat


def sub_assigner(db_id, pred_sql, gold_sql):
    if gold_sql not in sub_cache:
        sub = catter.get_sub_category(gold_sql)
        sub_cache[gold_sql] = sub.name
    else:
        sub = sub_cache[gold_sql]
    return sub


def main(in_file, out_file):
    process_scores(in_file, cat_assigner, 'cat', out_file)
    process_scores(out_file, sub_assigner, 'sub', out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
