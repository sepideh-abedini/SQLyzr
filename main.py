from src.dataset.validate import validate_dataset
from src.eval.configs import BIRD_DEV, BIRD_SMALL
from src.eval.evaluator import calc_scores, post_process_scores
from src.eval.run_model import run_din
from src.sqlyzr_conf import DIN_BIRD_SMALL, DIN_SPIDER_SMALL


def main():
    print("################# SQLyzr Productions #################")

    eval_conf = DIN_SPIDER_SMALL.eval_conf
    # eval_conf = DAIL_SPIDER_SMALL.eval_conf
    # eval_conf = DAIL_SPIDER_SMALL.eval_conf
    # eval_conf = DIN_BIRD_SMALL.eval_conf

    validate_dataset(eval_conf.dataset_config)

    run_din(eval_conf)

    # run_dail(eval_conf)
    #
    calc_scores(eval_conf)

    post_process_scores(eval_conf)
    #
    # find_transformers(eval_conf)
    #
    # augment_data(DIN_SPIDER_SMALL)


if __name__ == '__main__':
    main()
