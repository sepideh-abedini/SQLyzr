from typing import Optional

from src.eval.dataset_config import DatasetConfig
from src.rel.db_facade import DatabaseFacade, SqliteFacade
from src.rel.mysql_facade import MysqlFacade


class DatabaseFactory:
    __instance: Optional[DatabaseFacade] = None

    @staticmethod
    def get_instance(conf: DatasetConfig):
        if not DatabaseFactory.__instance:
            instance = DatabaseFactory.get_new_instance_dangerous(conf)
            DatabaseFactory.__instance = instance
            return instance
        return DatabaseFactory.__instance

    @staticmethod
    def get_new_instance_dangerous(conf: DatasetConfig):
        if conf.dataset_type in ["bird", "spider"]:
            return SqliteFacade(conf)
        elif conf.dataset_type == "beaver":
            return MysqlFacade(conf)
        else:
            raise RuntimeError(f"No supported DB facade for dataset = {conf.dataset_type}")
