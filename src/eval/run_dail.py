import asyncio

from src.sqlyzr_conf import DIN_SPIDER_SMALL, DAIL_SPIDER_SMALL
from src.third_party.dail.ask_llm import run_dail, DailPredictor
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.data_preprocess import schema_linking_producer
from src.third_party.dail.generate_question import generate_questions


def main():
    eval_conf = DAIL_SPIDER_SMALL.eval_conf
    conf = DailConfig(eval_conf.get_runner_conf(0.0, 0))
    schema_linking_producer(conf)

    generate_questions(conf)

    dp = DailPredictor(conf)

    asyncio.run(dp.run())
    # run_dail(conf)
    print("Hello")


if __name__ == '__main__':
    main()
