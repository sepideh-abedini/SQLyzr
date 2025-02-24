import os
import sqlite3
from abc import ABC, abstractmethod
from functools import cache
from sqlite3 import Connection
from typing import List, Tuple, Optional, Dict

import aiosqlite
from loguru import logger

from src.eval.dataset_config import DatasetConfig

IN_MEM_DB = bool(int(os.environ.get("IN_MEM_DB", True)))

logger.info(f"In-memory database load: {IN_MEM_DB}")


class DatabaseFacade(ABC):
    conf: DatasetConfig

    def __init__(self, conf: DatasetConfig):
        self.conf = conf

    @abstractmethod
    def exec_query_sync(self, db_id: str, sql: str) -> Optional[List[Tuple]]:
        pass

    @abstractmethod
    async def exec_query_async(self, db_id: str, sql: str) -> Optional[List[Tuple]]:
        pass


class DatabaseFactory:
    __instance: Optional[DatabaseFacade] = None

    @staticmethod
    def get_instance(conf: DatasetConfig):
        if not DatabaseFactory.__instance:
            if conf.dataset_type in ["bird", "spider"]:
                DatabaseFactory.__instance = SqliteFacade(conf)
            else:
                raise RuntimeError(f"No supported DB facade for dataset = {conf.dataset_type}")
        return DatabaseFactory.__instance


class SqliteFacade(DatabaseFacade):
    sync_conns: Dict[str, Connection]
    file_conns: List[Connection]

    def __init__(self, conf: DatasetConfig):
        super().__init__(conf)
        self.sync_conns = dict()
        self.file_conns = []

    def get_sync_conn(self, db_id):
        if db_id not in self.sync_conns:
            conn = sqlite3.connect(f"file:{self.conf.get_db_file_path(db_id)}?mode=ro")
            if IN_MEM_DB:
                dest = sqlite3.connect(':memory:')
                conn.backup(dest)
                self.file_conns.append(conn)
                self.sync_conns[db_id] = dest
            else:
                self.sync_conns[db_id] = conn

        conn = self.sync_conns[db_id]
        return conn

    @cache
    def exec_query_sync(self, db_id: str, sql: str) -> Optional[List[Tuple]]:
        conn = self.get_sync_conn(db_id)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
        except Exception as e:
            logger.error(sql)
            logger.error(e)
            rows = None
        cursor.close()
        return rows

    async def exec_query_async(self, db_id: str, sql: str) -> Optional[List[Tuple]]:
        cursor = None
        conn = None
        try:
            conn = await aiosqlite.connect(self.conf.get_db_file_path(db_id))
            cursor = await conn.execute(sql)
            rows = await cursor.fetchall()
            return rows
        except Exception as e:
            logger.error(sql)
            logger.error(e)
            return None
        finally:
            if cursor:
                await cursor.close()
            if conn:
                await conn.interrupt()
                await conn.close()

    def __del__(self):
        for conn in self.sync_conns.values():
            conn.interrupt()
            conn.close()
        for conn in self.file_conns:
            conn.interrupt()
            conn.close()
