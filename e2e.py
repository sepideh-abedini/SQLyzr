import asyncio
from threading import Thread
import platform

import pandas as pd
import pytest

from src.mock_server import MockHTTPServer
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.file_utils import read_json
from src.util.log_util import configure_logging
import multiprocessing as mp


def get_overall_score(df, model, metric):
    return df.loc[(df['cat'] == 'all') & (df['model'] == model), metric].values[0]


async def e2e_test():
    conf_file = "e2e.json"
    configure_logging()
    server = MockHTTPServer(mock_data_dir="data/mock_data", conf=conf_file, host="localhost",
                            port=8888)
    t = Thread(target=server.start)
    t.start()
    configure_logging()
    sqlyzr = Sqlyzr(conf_file)
    await sqlyzr.run()
    df = pd.read_csv(sqlyzr.conf.eval_conf.get_scores_path())
    assert get_overall_score(df, 'dail', 'em_mean') == pytest.approx(0.21, abs=0.01)
    assert get_overall_score(df, 'din', 'em_mean') == pytest.approx(0.3, abs=0.01)
    assert get_overall_score(df, 'dail', 'rea_mean') == pytest.approx(0.45, abs=0.01)
    assert get_overall_score(df, 'din', 'rea_mean') == pytest.approx(0.47, abs=0.01)
    assert get_overall_score(df, 'dail', 'cc') == pytest.approx(0.63, abs=0.01)
    assert get_overall_score(df, 'din', 'cc') == pytest.approx(0.53, abs=0.01)
    server.stop()
    t.join()
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
    print("###### Congrats! E2E test complete #######")


def main():
    if platform.system() == "Linux":
        mp.set_start_method("spawn", force=True)
    asyncio.run(e2e_test())


if __name__ == '__main__':
    main()
