import os

import psutil
from pydantic import BaseModel, computed_field


class FileGeneratorUsage(BaseModel):
    total_time: float = 0
    total_tokens: int = 0

    @computed_field
    @property
    def cur_mem_mb(self) -> float:
        return self.__process.memory_info()[0] / float(2 ** 20)

    @computed_field
    @property
    def cur_cpu_time(self) -> float:
        return sum(self.__process.cpu_times())

    @property
    def __process(self):
        return psutil.Process(os.getpid())

    def __add__(self, other):
        if not isinstance(other, FileGeneratorUsage):
            raise RuntimeError(f"Invalid operand: {other}")
        return self.model_copy(update={
            "total_tokens": self.total_tokens + other.total_tokens,
            "total_time": self.total_time + other.total_time
        })

    def plus_time(self, time: float):
        return self.model_copy(update={
            "total_time": self.total_time + time
        })

    def plus_tokens(self, tokens: int):
        return self.model_copy(update={
            "total_tokens": self.total_tokens + tokens
        })
