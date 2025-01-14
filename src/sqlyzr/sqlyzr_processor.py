from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.configs.sqlyzr import SQLyzrConfig


@dataclass
class SqlyzrProcessor(ABC):
    conf: SQLyzrConfig
    enabled: bool

    @abstractmethod
    async def run(self):
        pass
