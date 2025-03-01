import os
import sys
from typing import Callable

from loguru import logger

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


def configure_logging():
    logger.remove(0)
    # logger.add(sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO").upper(), colorize=True,
    #            format="<green>{time:HH:mm:ss} | </green><level> {level}: {message}</level>")
    logger.add("info.log", level="INFO")
    logger.add("trace.log", level="DEBUG")
    logger.add("debug.log", level="DEBUG")
    logger.add("db.trace.log", level="TRACE",filter="src.rel.db_facade")
    logger.add("db.debug.log", level="DEBUG",filter="src.rel.db_facade")
    logger.add("post_process.trace.log", level="TRACE",filter="src.third_party.dail.utils.post_process")
    # logger.add(sys.stderr, level=LOG_LEVEL, colorize=True, enqueue=True, format="<green>{time:HH:mm:ss} | </green><cyan>[{module}:{function}:{line}]</cyan><level> {level}: {message}</level>")
    logger.add(sys.stderr, level=LOG_LEVEL, colorize=True, enqueue=True, format="<green>{time:HH:mm:ss} | </green><level> {level}: {message}</level>")


def trace(func: Callable):
    def wrapper(*args):
        logger.trace(f"{func.__module__}:{func.__name__}")
        func(*args)

    return wrapper
