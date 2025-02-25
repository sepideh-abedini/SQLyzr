import asyncio
import concurrent
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

import tqdm
from loguru import logger
from openai.types.chat import ChatCompletion

from src.eval.lib import Timer
from src.eval.single_run_config import SingleRunConfig
from src.gpt.models import BatchInputRequest
from src.pred.predictor import Predictor
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.data_preprocess import DailSchemaLinksGenerator
from src.third_party.dail.generate_question import DailQuestionGenerator
from src.third_party.dail.generate_second_question import DailSecondQuestionGenerator
from src.third_party.dail.utils.post_process import process_duplication, get_sqls
from src.util.async_utils import apply_async
from src.util.model_utils import read_jsonl
from src.util.multi_thread_utils import chunk_list, flatten, get_thread_pool, NUM_THREADS


class DailPredictor(Predictor):
    __conf: DailConfig
    __questions: List[str]

    def __init__(self, run_conf: SingleRunConfig):
        super().__init__(run_conf)
        self.__conf = DailConfig(run_conf.get_pred_path())

    async def _run_internal(self):
        schema_links_gen = DailSchemaLinksGenerator(self.__conf, self._run_conf)
        usage = schema_links_gen.run()
        self._tracker.add_usage(usage)
        logger.info("Schema linking done!")

        question_gen = DailQuestionGenerator(self.__conf, self._run_conf, self.__conf.questions_path())
        usage = question_gen.run()
        self._tracker.add_usage(usage)
        logger.info("Question generation done!")

        self.__load_questions(self.__conf.questions_path())
        self._gen_batch_file(self.__conf.get_path("in"), self.__gen_sql_req)
        await self._ask_file(self.__conf.get_path("in"), self.__conf.get_path("out"))
        logger.info("SQL generation done!")

        if os.path.exists(self.__conf.pre_test_result_path()):
            logger.debug(f"Pre test result exists: {self.__conf.pre_test_result_path()}")
            with open(self.__conf.pre_test_result_path()) as file:
                sqls = file.readlines()
        else:
            timer = Timer.start()
            sqls = self.__process_responses(self.__conf.get_path("out"))
            with open(self.__conf.pre_test_result_path(), "w") as file:
                for sql in sqls:
                    file.write(f"{sql}\n")
            lap = timer.lap()
            with open(f"{self.__conf.pre_test_result_path()}.usage", "w") as usage_file:
                usage_file.write(f"{lap}")

        second_question_gen = DailSecondQuestionGenerator(self.__conf, self._run_conf,
                                                          self.__conf.second_questions_path())
        usage = second_question_gen.run()
        self._tracker.add_usage(usage)
        logger.info("Second Question generation done!")

        self.__load_questions(self.__conf.second_questions_path())
        self._gen_batch_file(self.__conf.get_path("in.second"), self.__gen_sql_req)

        await self._ask_file(self.__conf.get_path("in.second"), self.__conf.get_path("out.second"))
        sqls = self.__process_responses(self.__conf.get_path("out.second"))
        logger.info("Second SQL generation done!")

        self._save_sqls(sqls)

    def __gen_sql_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        dail_question = self.__questions[i]
        request = self._create_batch_req(f"i{i}", dail_question, self.__conf.gpt_params)
        return request

    def __load_questions(self, path: str):
        questions_json = json.load(open(path, "r"))
        self.__questions = [_["prompt"] for _ in questions_json["questions"]]

    @staticmethod
    def __process_gpt_4o_mini_sql(content: str) -> str:
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

    def post_process_response(self, pairs: List[Tuple[str, ChatCompletion]]):
        results = []
        for i, pair in tqdm.tqdm(enumerate(pairs), total=len(pairs),
                                 desc=f"Processing SQLs {self._run_conf}"):
            db_id = pair[0]
            response = pair[1]
            contents = [choice.message.content for choice in response.choices]
            if self.__conf.gpt_params['n'] == 1:
                for sql in contents:
                    sql = " ".join(sql.replace("\n", " ").split())
                    sql = process_duplication(sql)
                    if sql.startswith("SELECT"):
                        results.append(sql + "\n")
                    elif sql.startswith(" "):
                        results.append("SELECT" + sql + "\n")
                    else:
                        results.append("SELECT " + sql + "\n")
            else:
                sqls = contents
                processed_sqls = []
                for sql in sqls:
                    sql = " ".join(sql.replace("\n", " ").split())
                    sql = process_duplication(sql)
                    sql = self.__process_gpt_4o_mini_sql(sql)
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
                results.extend(final_sqls)
        return results

    def __process_responses(self, file_path) -> List[str]:
        with open(self._run_conf.dataset_config.get_test_path()) as data_file:
            data = json.load(data_file)
            db_ids = [example['db_id'] for example in data]
        responses = read_jsonl(file_path, ChatCompletion)
        pairs = list(zip(db_ids, responses))
        chunks = chunk_list(pairs, NUM_THREADS)
        with get_thread_pool() as executor:
            result_chunks = list(executor.map(self.post_process_response, chunks))
        results = flatten(result_chunks)
        return results
