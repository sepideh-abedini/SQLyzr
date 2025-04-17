from typing import Optional, Dict

from src.eval.dataset_config import DatasetConfig
from src.rel.db_facade import DatabaseFacade, SqliteFacade
from src.rel.mysql_facade import MysqlFacade


class DatabaseFactory:
    __instances: Dict[str, DatabaseFacade] = dict()

    @staticmethod
    def get_instance(conf: DatasetConfig):
        if conf.dataset_type not in DatabaseFactory.__instances:
            instance = DatabaseFactory.get_new_instance_dangerous(conf)
            DatabaseFactory.__instances[conf.dataset_type] = instance
        return DatabaseFactory.__instances[conf.dataset_type]

    @staticmethod
    def get_new_instance_dangerous(conf: DatasetConfig):
        if conf.dataset_type in ["bird", "spider"]:
            return SqliteFacade(conf)
        elif conf.dataset_type == "beaver":
            return MysqlFacade(conf)
        else:
            raise RuntimeError(f"No supported DB facade for dataset = {conf.dataset_type}")
