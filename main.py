import asyncio

from src.aug.example_generator import generate_examples
from src.cat.categories import CAT_4
from src.eval.configs import DIN_SMALL_CONF
from src.eval.evaluator import calc_scores
from src.third_party.din.din_pred import DinPredictor


def main():
    print("################# SQLyzr Productions #################")
    for conf in DIN_SMALL_CONF.get_run_confs():
        predictor = DinPredictor(conf)
        asyncio.run(predictor.run())

    calc_scores(DIN_SMALL_CONF)

    generate_examples(CAT_4, "concert_singer")


if __name__ == '__main__':
    main()
