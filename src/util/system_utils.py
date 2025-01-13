import json
import os
from typing import Any, Dict

import psutil
from pydantic import BaseModel, computed_field


class UsageInfo(BaseModel):
    mem_mb: float
    cpu_time: float


class ProcessUsage:
    def __init__(self):
        self.process = psutil.Process(os.getpid())

    @property
    def mem_mb(self) -> float:
        return self.process.memory_info()[0] / float(2 ** 20)

    @property
    def cpu_time(self) -> float:
        return sum(self.process.cpu_times())

    def to_dict(self) -> Dict[str, float]:
        d = dict()
        for attr_name in dir(type(self)):
            attr = getattr(type(self), attr_name)
            if isinstance(attr, property):
                d[attr_name] = getattr(self, attr_name)
        return d

    def dump(self, out_path: str):
        with open(out_path, "w") as file:
            file.write(json.dumps(self.to_dict(), indent=4))

    @staticmethod
    def dump_proc_usage(out_path: str):
        usage = ProcessUsage()
        usage.dump(out_path)


def save_usage_info(out_path: str):
    # return the memory usage in MB
    # print(process.cpu_times())
    # process.
    # print(process.memory_info())
    # process.cpu_times()
    # mem = p
    # return mem
    return 0
