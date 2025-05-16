import asyncio
from threading import Thread

import pandas as pd
import pytest

from src.app_setup import setup_app
from src.mock_server import MockHTTPServer
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.file_utils import read_json
from src.util.log_util import configure_logging


def get_overall_score(df, model, metric):
    score = df.loc[(df['cat'] == 'all') & (df['model'] == model), metric].values[0]
    print(f"Model: {model}, Metric: {metric}, Score: {score}")
    return score


async def run_sqlyzr(conf_file: str):
    sqlyzr = Sqlyzr(conf_file)
    await sqlyzr.run()
    df = pd.read_csv(sqlyzr.conf.eval_conf.get_scores_path())
    assert get_overall_score(df, 'dail', 'em_mean') == pytest.approx(0.17, abs=0.02)
    assert get_overall_score(df, 'din', 'em_mean') == pytest.approx(0.3, abs=0.02)
    assert get_overall_score(df, 'dail', 'rea_mean') == pytest.approx(0.41, abs=0.02)
    assert get_overall_score(df, 'din', 'rea_mean') == pytest.approx(0.47, abs=0.02)
    assert get_overall_score(df, 'dail', 'cc') == pytest.approx(0.63, abs=0.02)
    assert get_overall_score(df, 'din', 'cc') == pytest.approx(0.53, abs=0.02)
    trs_path = None
    for conf in sqlyzr.conf.eval_conf.get_run_confs():
        if "bird" in conf.get_pred_path():
            trs_path = conf.get_trs_path()
    assert trs_path is not None
    repair_data = read_json(trs_path + ".json")
    repair_messages = list(map(lambda r: r["messages"][0], repair_data))
    print(repair_messages)

    assert repair_messages == ['The predicted SQL has extra rows in the result set.',
                               'The predicted SQL used extra columns that should be removed.',
                               'The predicted SQL used extra columns that should be removed.']
    print("Assertions complete!")


async def e2e_test():
    conf_file = "e2e.json"
    # configure_logging()
    # server = MockHTTPServer(mock_data_dir="data/mock_data", conf=conf_file, host="localhost", port=8888)
    # t = Thread(target=server.start)
    # t.start()
    # try:
    await run_sqlyzr(conf_file)
    print("###### Congrats! E2E test complete #######")
    # finally:
    # server.stop()
    # t.join()


def main():
    asyncio.run(e2e_test())


if __name__ == '__main__':
    setup_app()
    main()
