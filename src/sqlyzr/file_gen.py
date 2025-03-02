import os
from abc import abstractmethod, ABC

from loguru import logger

from src.eval.lib import TimeLogger


class FileGenerator(ABC):
    _out_path: str

    def __init__(self, out_path):
        self._out_path = out_path

    def run(self):
        if os.path.exists(self._out_path):
            logger.info(f"File exists: {self._out_path}, skipping!")
            return
        time_logger = TimeLogger.start(f"DAIL:{self.__class__.__name__}")
        self._run_internal()
        time_logger.lap()

    @abstractmethod
    def _run_internal(self):
        pass
