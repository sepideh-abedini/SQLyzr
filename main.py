from src.eval.configs import DIN_SMALL_CONF
from src.eval.evaluator import calc_scores, post_process_scores
from src.rel.transformer_eval import find_transformers


def main():
    print("################# SQLyzr Productions #################")

    conf = DIN_SMALL_CONF

    # run_din(conf)

    # calc_scores(conf)

    post_process_scores(conf)

    # find_transformers(conf)

    # augment_data(conf)


if __name__ == '__main__':
    main()
