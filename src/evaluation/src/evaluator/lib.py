import datetime
import math
import sqlite3
import subprocess

import pandas as pd

LOG_LEVEL = 'DEBUG'


class Timer():
    def __init__(self):
        pass

    def start(self):
        self.start_time = datetime.datetime.now()

    def stop(self):
        return datetime.datetime.now() - self.start_time


def log(*args):
    if LOG_LEVEL == 'DEBUG':
        print(*args)


def confidence_level_interval(column: pd.Series) -> float:
    CONFIDENCE = 0.95
    Z = 1.65
    SE = column.std() / math.sqrt(column.size)
    err_margin = Z * SE
    mean = column.mean()
    interval_start = mean - err_margin
    interval_end = mean + err_margin
    return "({:.3f}, {:.3f})".format(interval_start, interval_end)


def exec_sql(db_path, sql):
    """
    return 1 if the values between prediction and gold are matching
    in the corresponding index. Currently, not support multiple col_unit(pairs).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        return res
    except sqlite3.OperationalError as e:
        print(e)
        return False


def execute_command(command: str):
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        output, errors = p.communicate()
        print(output, errors)
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)
