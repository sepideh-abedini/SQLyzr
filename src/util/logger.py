import os
from enum import Enum


class LogLevel(Enum):
    ERROR = 3
    INFO = 2
    DEBUG = 1


LOG_LEVEL = LogLevel[os.environ.get("LOG_LEVEL", "INFO").upper()]


def log(msg, msg_level: LOG_LEVEL = LogLevel.INFO):
    if msg_level.value >= LOG_LEVEL.value:
        print(msg)


def debug_log(msg):
    log(msg, LOG_LEVEL.DEBUG)
