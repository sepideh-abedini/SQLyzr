import datetime
import os
from datetime import datetime, timedelta

import math
import sqlite3
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
    CONFIDENCE = 0.95
    Z = 1.65
    SE = column.std() / math.sqrt(column.size)
    err_margin = Z * SE
    mean = column.mean()
    interval_start = mean - err_margin
    interval_end = mean + err_margin
    return "({:.2f}%, {:.2f}%)".format(interval_start * 100, interval_end * 100)
    # return f"({interval_start}, {interval_end})"


class DatabaseClient:
    config: DatasetConfig

    def __init__(self, config: DatasetConfig):
        self.config = config

    def exec_mysql(self, db_id, sql):
        connection = mysql.connector.connect(
            host="localhost",
            user=os.getenv("MYSQL_USERNAME"),
            password=os.getenv("MYSQL_PASSWORD"),
            db=db_id
        )

        cursor = connection.cursor()
        try:
            # Execute the SQL query
            cursor.execute(sql)
            res = cursor.fetchall()
            return res
        except Exception as err:
            print(sql)
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()
            connection.close()

    # FIXME:
    def clean(self, sql: str) -> str:
        sql = sql.replace("\n", "")
        sql = sql.replace("\\n", "")
        return sql

    def exec_sql(self, db_id, sql):
        sql = self.clean(sql)
        if self.config.mysql:
            return self.exec_mysql(db_id, sql)

        db_path = self.config.get_db_file_path(db_id)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            return res
        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
            logger.debug(e)
            return None


def execute_command(command: str):
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        output, errors = p.communicate()
        print(output, errors)
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)
