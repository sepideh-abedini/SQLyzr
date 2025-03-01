import hashlib
import os

from diskcache import Cache

cache = Cache("/tmp/tmp_cache")


def sqls_equal(a: str, b: str):
    a = a.strip()
    b = b.strip()
    return a == b


def lookup_db_cache(db_id, sql):
    sql_hash = f"{db_id}_{sql}"
    if sql_hash in cache:
        return cache[sql_hash]
    return None


def save_db_cache(db_id, sql, result):
    sql_hash = f"{db_id}_{sql}"
    cache[sql_hash] = result


def sha256_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


if not os.path.exists("/tmp/scache"):
    os.mkdir("/tmp/scache")
