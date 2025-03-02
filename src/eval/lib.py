import datetime
import os
from datetime import datetime, timedelta

import math
import subprocess
import mysql.connector

from loguru import logger

import pandas as pd

from src.eval.dataset_config import DatasetConfig


class Timer:
    start_time: datetime

    def __init__(self):
        self.start_time = datetime.now()

    @staticmethod
    def start():
        return Timer()

    def lap(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()


def confidence_level_interval(column: pd.Series) -> str:
    if not pd.api.types.is_numeric_dtype(column):
        return "NA"
    CONFIDENCE = 0.95
    Z = 1.65
    SE = column.std() / math.sqrt(column.size)
    err_margin = Z * SE
    mean = column.mean()
    interval_start = mean - err_margin
    interval_end = mean + err_margin
    return "({:.2f}%, {:.2f}%)".format(interval_start * 100, interval_end * 100)
    # return f"({interval_start}, {interval_end})"


def execute_command(command: str):
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        output, errors = p.communicate()
        print(output, errors)
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)
