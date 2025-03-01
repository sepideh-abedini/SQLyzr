import hashlib
import json
import os
from dataclasses import dataclass
from typing import Set
from diskcache import Cache

from loguru import logger

cache = Cache("/tmp/tmp_cache")


def sqls_equal(a: str, b: str):
    a = a.strip()
    b = b.strip()
    return a == b


@dataclass(frozen=True)
class CachePath:
    CACHE_DIR = "/tmp/db_cache"
    SQLS_FILE = "sql_ids.txt"

    @staticmethod
    def sql_dir(db_id, sql):
        sql_hash = sha256_hash(sql)
        return os.path.join(CachePath.CACHE_DIR, db_id, sql_hash)

    @staticmethod
    def sql_ids_path(db_id, sql):
        return os.path.join(CachePath.sql_dir(db_id, sql), CachePath.SQLS_FILE)

    @staticmethod
    def res_path(db_id, sql, i):
        return os.path.join(CachePath.sql_dir(db_id, sql), f"res_{i}.json")


def lookup_sql_id(db_id, sql: str) -> Set[int]:
    sql_ids_path = CachePath.sql_ids_path(db_id, sql)
    if not os.path.exists(sql_ids_path):
        return set()
    with open(sql_ids_path, 'r') as file:
        sqls = file.readlines()
    all_ids = set()
    for i, cached_sql in enumerate(sqls):
        if sqls_equal(cached_sql, sql):
            all_ids.add(i)
    return all_ids


def get_id_res(db_id, sql, sql_id):
    res_path = CachePath.res_path(db_id, sql, sql_id)
    if not os.path.exists(res_path):
        return None
    with open(res_path, 'r') as file:
        rows = json.load(file)
        if rows is None:
            return None
        return list(map(tuple, rows))


def lookup_db_cache_unsafe(db_id, sql):
    ids = lookup_sql_id(db_id, sql)
    if len(ids) == 0:
        return None
    res = None
    for i in ids:
        res = get_id_res(db_id, sql, i)
        if res is None:
            continue
    return res


def lookup_db_cache(db_id, sql):
    sql_hash = f"{db_id}_{sql}"
    if sql_hash in cache:
        return cache[sql_hash]
    return None
    # try:
    #     return lookup_db_cache_unsafe(db_id, sql)
    # except Exception as e:
    #     logger.error(f"Cache lookup error: {e}")
    #     pass


def save_db_cache_unsafe(db_id, sql, result):
    sql_ids_path = CachePath.sql_ids_path(db_id, sql)
    os.makedirs(CachePath.sql_dir(db_id, sql), exist_ok=True)
    if os.path.exists(sql_ids_path):
        with open(sql_ids_path, 'r') as sql_ids_file:
            num_sqls = len(sql_ids_file.readlines())
    else:
        num_sqls = 0
    with open(sql_ids_path, 'a') as sql_ids_file:
        sql_ids_file.write(f"{sql}\n")
    res_path = CachePath.res_path(db_id, sql, num_sqls)
    with open(res_path, 'w') as res_file:
        res_file.write(json.dumps(result, indent=4))


def save_db_cache(db_id, sql, result):
    sql_hash = f"{db_id}_{sql}"
    cache[sql_hash] = result
    # if sql_hash not inccache:
    #     cache[sql_hash] = [result]
    # data = cache[sql_hash]
    # data = data + [sql]
    # cache[sql_hash] = data
    # try:
    #     save_db_cache_unsafe(db_id, sql, result)
    # except Exception as e:
    #     logger.error(f"Cache save error: {e}")
    #     pass


def sha256_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


if not os.path.exists("/tmp/scache"):
    os.mkdir("/tmp/scache")
