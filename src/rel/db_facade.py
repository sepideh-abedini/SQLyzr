import os
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from src.eval.dataset_config import DatasetConfig

IN_MEM_DB = False

DB_TIMEOUT = int(os.environ.get("DB_TIMEOUT", 60_000))
DB_CACHE = bool(int(os.environ.get("DB_CACHE", 0)))


class DatabaseFacade(ABC):
    conf: DatasetConfig

    def __init__(self, conf: DatasetConfig):
        self.conf = conf

    @abstractmethod
    def check_connection(self):
        pass

    @abstractmethod
    def exec_query_sync(self, db_id: str, sql: str, timeout: int = DB_TIMEOUT) -> Optional[List[Tuple]]:
        pass

    @abstractmethod
    def exec_query_uncached(self, db_id: str, sql: str, timeout: int = DB_TIMEOUT) -> Optional[List[Tuple]]:
        pass

    @abstractmethod
    def get_tables(self, db_id):
        pass

    @abstractmethod
    def get_primary_key(self, db_id, table_name):
        pass

    @abstractmethod
    def get_foreign_key(self, db_id, table_name):
        pass

    @abstractmethod
    def get_col_names(self, db_id, table_name):
        pass

    @abstractmethod
    def get_create_sql(self, db_id, table_name):
        pass
