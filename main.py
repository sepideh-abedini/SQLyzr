from src.aug.augment_data import augment_data
from src.eval.evaluator import calc_scores, post_process_scores
from src.eval.run_model import run_din
from src.rel.transformer_eval import find_transformers
from src.sqlyzr_conf import DIN_SPIDER_SMALL


def main():
    print("################# SQLyzr Productions #################")

    eval_conf = DIN_SPIDER_SMALL.eval_conf

    run_din(eval_conf)

    calc_scores(eval_conf)

    post_process_scores(eval_conf)

    find_transformers(eval_conf)

    augment_data(DIN_SPIDER_SMALL)


if __name__ == '__main__':
    main()
