from typing import Optional

from src.eval.dataset_config import DatasetConfig
from src.rel.db_facade import DatabaseFacade, SqliteFacade
from src.rel.mysql_facade import MysqlFacade


class DatabaseFactory:
    __instance: Optional[DatabaseFacade] = None

    @staticmethod
    def get_instance(conf: DatasetConfig):
        if not DatabaseFactory.__instance:
            if conf.dataset_type in ["bird", "spider"]:
                DatabaseFactory.__instance = SqliteFacade(conf)
            elif conf.dataset_type == "beaver":
                DatabaseFactory.__instance = MysqlFacade(conf)
            else:
                raise RuntimeError(f"No supported DB facade for dataset = {conf.dataset_type}")
        return DatabaseFactory.__instance
