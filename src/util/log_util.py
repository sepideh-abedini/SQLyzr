import functools
import os
import sys
from typing import Callable, TypedDict, Any

from loguru import logger

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


class TimingLogData(TypedDict):
    idx: str
    start: bool


def filter_timing(record):
    return 'idx' in record['extra']


def configure_logging():
    try:
        logger.remove(0)
    except Exception:
        pass
    logger.add("std.log", level="INFO")
    # logger.add(sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO").upper(), colorize=True,
    #            format="<green>{time:HH:mm:ss} | </green><level> {level}: {message}</level>")
    # logger.add("timing.jsonl", level="INFO", filter=filter_timing, serialize=True)
    # logger.add("timing.log", level="INFO", filter=filter_timing, colorize=True,
    #            format="<green>{time:HH:mm:ss}[{process.id}] | </green><level> {level}: [{extra[idx]}] {message}</level>")
    # logger.add("info.log", level="INFO")
    # logger.add("trace.log", level="DEBUG")
    # logger.add("debug.log", level="DEBUG")
    # logger.add("db.trace.log", level="TRACE", filter="src.rel.db_facade")
    # logger.add("db.debug.log", level="DEBUG", filter="src.rel.db_facade")
    # logger.add("post_process.trace.log", level="TRACE", filter="src.third_party.dail.utils.post_process")
    # logger.add(sys.stderr, level=LOG_LEVEL, colorize=True, enqueue=True, format="<green>{time:HH:mm:ss} | </green><cyan>[{module}:{function}:{line}]</cyan><level> {level}: {message}</level>")
    logger.add(sys.stderr, level=LOG_LEVEL, colorize=True, enqueue=True,
               format="<green>{time:HH:mm:ss}[{process.id}] | </green><level> {level}: {message}</level>")


def trace(func: Callable):
    def wrapper(*args):
        logger.trace(f"{func.__module__}:{func.__name__}")
        func(*args)

    return wrapper


def log(name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"[{name}] Starting!")
            result = func(*args, **kwargs)
            logger.info(f"[{name}] Finished!")
            return result

        return wrapper

    return decorator


def alog(name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            logger.info(f"[{name}] Starting!")
            result = await func(*args, **kwargs)
            logger.info(f"[{name}] Finished!")
            return result

        return wrapper

    return decorator


_LOGGING_CONFIGURED = False
if not _LOGGING_CONFIGURED:
    configure_logging()
    logger.info(f"Logging configured!")
    _LOGGING_CONFIGURED = True
