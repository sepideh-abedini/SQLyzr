import re
from typing import List, Tuple

from diskcache import Cache
from openai.types.chat import ChatCompletion
import tqdm

from src.eval.single_run_config import SingleRunConfig
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.utils.post_process import process_duplication, get_sqls

CACHE_DIR = "/tmp/dail_post_processor"


class DailSqlPostProcessorWorker:
    __conf: DailConfig
    _run_conf: SingleRunConfig

    def __init__(self, conf: DailConfig, run_conf: SingleRunConfig):
        self.__conf = conf
        self._run_conf = run_conf
        self.cache = Cache(CACHE_DIR)

    def post_proc_single(self, pair: Tuple[str, ChatCompletion]):
        result = ""
        db_id = pair[0]
        response = pair[1]
        if response.id in self.cache:
            return self.cache[response.id]
        contents = [choice.message.content for choice in response.choices]
        if self.__conf.gpt_params['n'] == 1:
            for sql in contents:
                sql = " ".join(sql.replace("\n", " ").split())
                sql = process_duplication(sql)
                if sql.startswith("SELECT"):
                    result = sql + "\n"
                elif sql.startswith(" "):
                    result = "SELECT" + sql + "\n"
                else:
                    result = "SELECT " + sql + "\n"
        else:
            sqls = contents
            processed_sqls = []
            for sql in sqls:
                sql = " ".join(sql.replace("\n", " ").split())
                sql = process_duplication(sql)
                sql = process_gpt_4o_mini_sql(sql)
                if sql.startswith("SELECT"):
                    pass
                elif sql.startswith(" "):
                    sql = "SELECT" + sql
                else:
                    sql = "SELECT " + sql
                processed_sqls.append(sql)
            result = {
                'db_id': db_id,
                'p_sqls': processed_sqls
            }
            final_sqls = get_sqls([result], self.__conf.gpt_params['n'],
                                  self._run_conf.dataset_config)
            result = final_sqls[0]
        self.cache[response.id] = result
        return result

    def post_process_response(self, pairs: List[Tuple[str, ChatCompletion]]):
        results = []
        for i, pair in tqdm.tqdm(enumerate(pairs), total=len(pairs),
                                 desc=f"Processing SQLs {self._run_conf}"):
            result = self.post_proc_single(pair)
            results.append(result)
        return results


def process_gpt_4o_mini_sql(content: str) -> str:
    content = content.strip()
    content = content.replace("\n", " ")
    if "SQL:" in content:
        pattern = r'.*SQL:[\s`]*(SELECT.*)[\s`]*'
        content = re.sub(pattern, r'\1', content, flags=re.DOTALL)
    if "```sql" in content:
        pattern = r'.*```sql(.*)```.*'
        content = re.sub(pattern, r'\1', content, flags=re.DOTALL)
    content = content.strip()
    return content
