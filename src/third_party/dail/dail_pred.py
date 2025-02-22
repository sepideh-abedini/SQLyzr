import json
import os
import re
from typing import List

from openai.types.chat import ChatCompletion

from src.eval.single_run_config import SingleRunConfig
from src.gpt.models import BatchInputRequest
from src.pred.predictor import Predictor
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.data_preprocess import DailSchemaLinksGenerator
from src.third_party.dail.generate_question import DailQuestionGenerator, DailParams
from src.third_party.dail.generate_second_question import DailSecondQuestionGenerator
from src.third_party.dail.utils.post_process import process_duplication, get_sqls
from src.util.model_utils import read_jsonl


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

        question_gen = DailQuestionGenerator(self.__conf, self._run_conf, self.__conf.questions_path())
        usage = question_gen.run()
        self._tracker.add_usage(usage)

        self.__load_questions(self.__conf.questions_path())
        self._gen_batch_file(self.__conf.get_path("in"), self.__gen_sql_req)
        await self._ask_file(self.__conf.get_path("in"), self.__conf.get_path("out"))

        sqls = await self.__process_responses(self.__conf.get_path("out"))
        with open(self.__conf.pre_test_result_path(), "w") as file:
            for sql in sqls:
                file.write(f"{sql}\n")

        second_question_gen = DailSecondQuestionGenerator(self.__conf, self._run_conf,self.__conf.second_questions_path())
        usage = second_question_gen.run()
        self._tracker.add_usage(usage)

        self.__load_questions(self.__conf.second_questions_path())
        self._gen_batch_file(self.__conf.get_path("in.second"), self.__gen_sql_req)
        await self._ask_file(self.__conf.get_path("in.second"), self.__conf.get_path("out.second"))
        sqls = await self.__process_responses(self.__conf.get_path("out.second"))

        self._save_sqls(sqls)

    def __gen_sql_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        dail_question = self.__questions[i]
        request = self._create_batch_req(f"i{i}", dail_question, self.__conf.params)
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
            content = re.sub(pattern, r'\1', content)
        if "```sql" in content:
            pattern = r'.*```sql\s*(SELECT.*)\s*```.*'
            content = re.sub(pattern, r'\1', content)
        return content

    async def __process_responses(self, file_path) -> List[str]:
        with open(self._run_conf.dataset_config.get_test_path()) as data_file:
            data = json.load(data_file)
            db_ids = [example['db_id'] for example in data]
        responses = read_jsonl(file_path, ChatCompletion)
        results = []
        for i, response in enumerate(responses):
            contents = [choice.message.content for choice in response.choices]
            if self.__conf.params['n'] == 1:
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
                db_id = db_ids[i]
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
                final_sqls = await get_sqls([result], self.__conf.params['n'],
                                            self._run_conf.dataset_config.get_db_path())
                results.extend(final_sqls)
        return results
