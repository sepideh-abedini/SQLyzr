from threading import Thread

import pandas as pd
import pytest

from src.mock_server import MockHTTPServer
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.log_util import configure_logging


async def test_sqlyzr():
    server = MockHTTPServer(config_file="src/mock_server/config.json", host="localhost", port=8888)
    t = Thread(target=server.start)
    t.start()
    configure_logging()
    sqlyzr = Sqlyzr("tests/e2e.json")
    await sqlyzr.run()
    server.stop()
    t.join()
    df = pd.read_csv(sqlyzr.conf.eval_conf.get_scores_path())
    assert df.loc[df['cat'] == 'all', 'rea_mean'].values[0] == 0.8
