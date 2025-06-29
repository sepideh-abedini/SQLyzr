import argparse

from src.cat.categories import SUB_INF
from src.cat.catter import Catter
from src.util.log_util import configure_logging
from thesis_latest.lib.score_lib import process_scores

configure_logging()
catter = Catter()


def cat_assigner(db_id, pred_sql, gold_sql):
    cat = catter.get_category(pred_sql)
    return cat


def sub_assigner(db_id, pred_sql, gold_sql):
    try:
        sub = catter.get_sub_category(pred_sql)
    except:
        sub = SUB_INF
    return sub.name


def main(in_file, out_file):
    # process_scores(in_file, cat_assigner, 'pcat', out_file)
    process_scores(out_file, sub_assigner, 'psub', out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
