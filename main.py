import asyncio

from src.din.din_pred import DinPredictor
from src.eval.configs import DIN_SMALL_CONF
from src.eval.data_generator import export_evaluation_data, split_by_categories


def main():
    print("################# SQLyzr Productions #################")
    for conf in DIN_SMALL_CONF.get_run_confs():
        predictor = DinPredictor(conf)
        asyncio.run(predictor.run())
        export_evaluation_data(conf)
        split_by_categories(conf)


if __name__ == '__main__':
    main()
