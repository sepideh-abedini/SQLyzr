import os
import time
from dataclasses import dataclass
from threading import Thread

import psutil
from pydantic import BaseModel, computed_field
from src.sqlyzr.file_sender_usage import FileGeneratorUsage
from src.util.model_utils import write_model, read_model


class ResourceUsage(BaseModel):
    time: int = 0
    mem: float = 0
    cpu: float = 0
    tokens: int = 0

    @staticmethod
    def cur_mem_mb() -> float:
        return ResourceUsage.process().memory_info()[0] / float(2 ** 20)

    @staticmethod
    def cur_cpu_time() -> float:
        return sum(ResourceUsage.process().cpu_times())

    @staticmethod
    def process() -> psutil.Process:
        return psutil.Process(os.getpid())

    @staticmethod
    def cur_seconds() -> int:
        return int(time.time())

    @staticmethod
    def cur():
        return ResourceUsage(
            time=ResourceUsage.cur_seconds(),
            mem=ResourceUsage.cur_mem_mb(),
            cpu=ResourceUsage.cur_cpu_time(),
            tokens=0
        )

    def __add__(self, other):
        if not isinstance(other, ResourceUsage):
            raise RuntimeError(f"Invalid operand: {other}")
        return self.model_copy(update={
            "time": self.time + other.time,
            "mem": max(self.mem, other.mem),
            "cpu": self.cpu + other.cpu,
            "tokens": self.tokens + other.tokens
        })

    def __sub__(self, other):
        if not isinstance(other, ResourceUsage):
            raise RuntimeError(f"Invalid operand: {other}")
        return self.model_copy(update={
            "time": self.time - other.time,
            "mem": max(self.mem, other.mem),
            "cpu": self.cpu - other.cpu,
            "tokens": self.tokens + other.tokens
        })


class ResourceUsageTracker:
    __usage: ResourceUsage
    __last_usage: ResourceUsage
    __thread: Thread
    __max_mem: float
    __cond: bool = True

    def __init__(self, file_path: str):
        self.__file_path = file_path
        self.__usage = ResourceUsage()

    @property
    def usage_path(self):
        return f"{self.__file_path}.usage.json"

    def __track_mem(self):
        while self.__cond:
            self.__max_mem = max(self.__usage.mem, self.__max_mem)
            time.sleep(1)

    def start(self):
        self.__last_usage = ResourceUsage.cur()

    def lap_time(self):
        cur_usage = ResourceUsage.cur()
        last_usage = self.__last_usage
        self.__usage += cur_usage - last_usage

    def save_usage(self):
        write_model(self.__usage, self.usage_path)
        return self.__usage

    def load_usage(self) -> ResourceUsage:
        self.__usage = read_model(self.usage_path, ResourceUsage)
        return self.__usage

    def add_usage(self, usage: ResourceUsage):
        self.__usage += usage


class UsageTracker:
    __usage: FileGeneratorUsage
    __file_path: str

    def __init__(self, file_path: str):
        self.__file_path = file_path
        self.__usage = FileGeneratorUsage()

    @property
    def usage_path(self):
        return f"{self.__file_path}.usage.json"

    def add_time(self, time: float):
        self.__usage = self.__usage.plus_time(time)

    def add_tokens(self, tokens: int):
        self.__usage = self.__usage.plus_tokens(tokens)

    def add_usage(self, usage: FileGeneratorUsage):
        self.__usage += usage

    def save_usage(self):
        write_model(self.__usage, self.usage_path)
        return self.__usage

    def load_usage(self) -> FileGeneratorUsage:
        self.__usage = read_model(self.usage_path, FileGeneratorUsage)
        return self.__usage

    def start(self):
        pass
