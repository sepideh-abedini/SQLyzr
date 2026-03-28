import asyncio
import math
import os
import random
import re
import threading
from collections import defaultdict
from itertools import product
from typing import Tuple, Any, List, Set, Iterable

import sqlparse
from loguru import logger

from src.eval.dataset_config import DatasetConfig
from src.db.db_factory import DatabaseFactory


# process the case of duplicated output of ChatGPT and GPT4 for SQL Representation with QA or SQLONLY Organization
def process_duplication(sql):
    sql = sql.strip().split("/*")[0]
    return sql


threadLock = threading.Lock()
TIMEOUT = 60
EXEC_TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")


def permute_tuple(element: Tuple, perm: Tuple) -> Tuple:
    assert len(element) == len(perm)
    return tuple([element[i] for i in perm])


def unorder_row(row: Tuple) -> Tuple:
    return tuple(sorted(row, key=lambda x: str(x) + str(type(x))))


# unorder each row in the table
# [result_1 and result_2 has the same bag of unordered row]
# is a necessary condition of
# [result_1 and result_2 are equivalent in denotation]
def quick_rej(result1: List[Tuple], result2: List[Tuple], order_matters: bool) -> bool:
    s1 = [unorder_row(row) for row in result1]
    s2 = [unorder_row(row) for row in result2]
    if order_matters:
        return s1 == s2
    else:
        return set(s1) == set(s2)


# return whether two bag of relations are equivalent
def multiset_eq(l1: List, l2: List) -> bool:
    if len(l1) != len(l2):
        return False
    d = defaultdict(int)
    for e in l1:
        d[e] = d[e] + 1
    for e in l2:
        d[e] = d[e] - 1
        if d[e] < 0:
            return False
    return True


def get_constraint_permutation(tab1_sets_by_columns: List[Set], result2: List[Tuple]) -> Tuple[Iterable, int]:
    num_cols = len(result2[0])
    perm_constraints = [{i for i in range(num_cols)} for _ in range(num_cols)]
    result_len = math.prod(map(len, perm_constraints))
    if num_cols <= 3:
        return product(*perm_constraints), result_len

    # we sample 20 rows and constrain the space of permutations
    for _ in range(20):
        random_tab2_row = random.choice(result2)

        for tab1_col in range(num_cols):
            for tab2_col in set(perm_constraints[tab1_col]):
                if random_tab2_row[tab2_col] not in tab1_sets_by_columns[tab1_col]:
                    perm_constraints[tab1_col].remove(tab2_col)
    result_len = math.prod(map(len, perm_constraints))
    result = product(*perm_constraints)
    return result, result_len


# check whether two denotations are correct
def result_eq(result1: List[Tuple], result2: List[Tuple], order_matters: bool) -> bool:
    if len(result1) == 0 and len(result2) == 0:
        return True

    # if length is not the same, then they are definitely different bag of rows
    if len(result1) != len(result2):
        return False

    num_cols = len(result1[0])

    # if the results do not have the same number of columns, they are different
    if len(result2[0]) != num_cols:
        return False

    # unorder each row and compare whether the denotation is the same
    # this can already find most pair of denotations that are different
    if not quick_rej(result1, result2, order_matters):
        return False

    # the rest of the problem is in fact more complicated than one might think
    # we want to find a permutation of column order and a permutation of row order,
    # s.t. result_1 is the same as result_2
    # we return true if we can find such column & row permutations
    # and false if we cannot
    tab1_sets_by_columns = [{row[i] for row in result1} for i in range(num_cols)]

    # on a high level, we enumerate all possible column permutations that might make result_1 == result_2
    # we decrease the size of the column permutation space by the function get_constraint_permutation
    # if one of the permutation make result_1, result_2 equivalent, then they are equivalent
    perms, len_perms = get_constraint_permutation(tab1_sets_by_columns, result2)
    if len_perms > 1_000_000:
        return False

    # for perm in tqdm.tqdm(perms, total=len_perms, desc="Checking perms"):
    for perm in perms:
        if len(perm) != len(set(perm)):
            continue
        if num_cols == 1:
            result2_perm = result2
        else:
            result2_perm = [permute_tuple(element, perm) for element in result2]
        if order_matters:
            if result1 == result2_perm:
                return True
        else:
            # in fact the first condition must hold if the second condition holds
            # but the first is way more efficient implementation-wise
            # and we use it to quickly reject impossible candidates
            if set(result1) == set(result2_perm) and multiset_eq(result1, result2_perm):
                return True
    return False


def replace_cur_year(query: str) -> str:
    return re.sub(
        "YEAR\s*\(\s*CURDATE\s*\(\s*\)\s*\)\s*", "2020", query, flags=re.IGNORECASE
    )


def exec_on_db(config: DatasetConfig, db_id: str, query: str) -> Tuple[str, Any]:
    facade = DatabaseFactory.get_instance(config)
    res = facade.exec_query_sync(db_id, query)
    if res is not None:
        return "result", res
    else:
        return "exception", None
    # query = replace_cur_year(query)
    # cursor = get_cursor_from_path(sqlite_path)
    # try:
    #     cursor.execute(query)
    #     result = cursor.fetchall()
    #     cursor.close()
    #     cursor.connection.close()
    #     return "result", result
    # except Exception as e:
    #     cursor.close()
    #     cursor.connection.close()
    #     return "exception", e


async def exec_on_db_timeout(config: DatasetConfig, db_id,
                             query: str, process_id: str = "", timeout: int = TIMEOUT
                             ) -> Tuple[str, Any]:
    try:
        async with asyncio.timeout(TIMEOUT):
            return exec_on_db(config, db_id, query)
    except asyncio.TimeoutError:
        logger.error("Timeout error")
        return ('exception', TimeoutError)
    except Exception as e:
        return ("exception", e)


# postprocess the model predictions to avoid execution errors
# e.g. removing spaces between ">" and "="
def postprocess(query: str) -> str:
    query = query.replace("> =", ">=").replace("< =", "<=").replace("! =", "!=")
    return query


def remove_distinct(s):
    toks = [t.value for t in list(sqlparse.parse(s)[0].flatten())]
    return "".join([t for t in toks if t.lower() != "distinct"])


def get_exec_output(
        config: DatasetConfig,
        db_id: str,
        sql: str,
        plug_value: bool = False,
        keep_distinct: bool = False,
        progress_bar_for_each_datapoint: bool = True,
):
    # post-process the prediction.
    # e.g. removing spaces between ">" and "="
    sql = postprocess(sql)

    if not keep_distinct:
        try:
            # if sqlparse can't parse p_str, we should not even try to execute it
            sql = remove_distinct(sql)
        except Exception as e:
            return "exception", []

    # flag, sql_denotation = exec_on_db_timeout(config, db_id, sql)
    flag, sql_denotation = exec_on_db(config, db_id, sql)
    return flag, sql_denotation


def get_sqls(results, select_number, config: DatasetConfig):
    db_ids = []
    all_p_sqls = []
    for item in results:
        p_sqls = []
        db_ids.append(item['db_id'])
        for i, x in enumerate(item['p_sqls']):
            p_sqls.append(x)
            if i + 1 == select_number:
                break
        all_p_sqls.append(p_sqls)
    chosen_p_sqls = []
    for i, db_id in enumerate(db_ids):
        p_sqls = all_p_sqls[i]
        cluster_sql_list = []
        map_sql2denotation = {}
        for i, sql in enumerate(p_sqls):
            flag, denotation = get_exec_output(config, db_id, sql)
            if flag == "exception":
                continue
            map_sql2denotation[sql] = denotation
            denotation_match = False

            for id, cluster in enumerate(cluster_sql_list):
                center_sql = cluster[0]
                if result_eq(map_sql2denotation[center_sql], denotation, False):
                    cluster_sql_list[id].append(sql)
                    denotation_match = True
                    break
            if not denotation_match:
                cluster_sql_list.append([sql])
        cluster_sql_list.sort(key=lambda x: len(x), reverse=True)
        if not cluster_sql_list:
            chosen_p_sqls.append(p_sqls[0])
        else:
            chosen_p_sqls.append(cluster_sql_list[0][0])

    # print("save chosen sqls and results...")

    return chosen_p_sqls
