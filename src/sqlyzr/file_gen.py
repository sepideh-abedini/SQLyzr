import os
from abc import abstractmethod, ABC

from loguru import logger

from src.eval.lib import Timer
from src.gpt.file_sender.usage_tracker import  ResourceUsageTracker
from src.sqlyzr.file_sender_usage import FileGeneratorUsage


class FileGenerator(ABC):
    _out_path: str
    _tracker: ResourceUsageTracker

    def __init__(self, out_path):
        self._out_path = out_path
        self._tracker = ResourceUsageTracker(self._out_path)

    def run(self):
        if os.path.exists(self._out_path):
            logger.info(f"File exists: {self._out_path}, skipping!")
            return self._tracker.load_usage()
        # self._tracker.start()
        self._run_internal()
        # self._tracker.lap_time()
        return self._tracker.save_usage()

    @abstractmethod
    def _run_internal(self):
        pass
