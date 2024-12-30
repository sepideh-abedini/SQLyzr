import asyncio

from src.aug.auger import Auger
from src.cat.categories import CAT_4, CAT_2
from src.eval.configs import DIN_SMALL_CONF
from src.eval.evaluator import calc_scores
from src.third_party.din.din_pred import DinPredictor


def main():
    print("################# SQLyzr Productions #################")
    # for conf in DIN_SMALL_CONF.get_run_confs():
    #     predictor = DinPredictor(conf)
    #     asyncio.run(predictor.run())
    #
    # calc_scores(DIN_SMALL_CONF)
    #
    auger = Auger("data/aug/gen.jsonl", CAT_2, "concert_singer", DIN_SMALL_CONF.dataset_config)
    asyncio.run(auger.run())


if __name__ == '__main__':
    main()
