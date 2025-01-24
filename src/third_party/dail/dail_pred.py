import json
import os
import re
from typing import List

from src.eval.single_run_config import SingleRunConfig
from src.gpt.gpt_from_file_sender import GptFromFileSender
from src.gpt.gpt_usage_stats import GptUsageStats
from src.gpt.models import BatchInputRequest
from src.gpt.utils import load_responses
from src.pred.predictor import Predictor
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.data_preprocess import schema_linking_producer
from src.third_party.dail.generate_question import generate_questions
from src.third_party.dail.utils.post_process import process_duplication, get_sqls


class DailPredictor(Predictor):
    conf: DailConfig
    gpt_sender: GptFromFileSender
    questions: List[str]

    def __init__(self, run_conf: SingleRunConfig):
        super().__init__(run_conf)
        self.conf = DailConfig(run_conf.get_pred_path())

    def gen_sql_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        dail_question = self.questions[i]
        request = self.create_batch_req(f"i{i}", dail_question, self.conf.params)
        return request

    def load_questions(self):
        questions_json = json.load(open(self.conf.questions_path(), "r"))
        self.questions = [_["prompt"] for _ in questions_json["questions"]]

    async def run(self):
        if os.path.exists(self.run_conf.get_pred_path()):
            return

        schema_linking_producer(self.conf, self.run_conf)

        generate_questions(self.conf, self.run_conf)

        self.load_questions()

        self.gen_batch_file(self.conf.get_path("in"), self.gen_sql_req)

        await self.ask_file(self.conf.get_path("in"), self.conf.get_path("out"))

        sqls = await self.process_responses(self.conf.get_path("out"))

        self.save_sqls(sqls)

    @staticmethod
    def process_gpt_4o_mini_sql(content: str) -> str:
        content = content.strip()
        content = content.replace("\n", " ")
        if "SQL:" in content:
            pattern = r'.*SQL:[\s`]*(SELECT.*)[\s`]*'
            content = re.sub(pattern, r'\1', content)
        if "```sql" in content:
            pattern = r'.*```sql\s*(SELECT.*)\s*```.*'
            content = re.sub(pattern, r'\1', content)
        return content

    async def process_responses(self, file_path) -> List[str]:
        with open(self.run_conf.dataset_config.get_data_path()) as data_file:
            data = json.load(data_file)
            db_ids = [example['db_id'] for example in data]
        responses = load_responses(file_path)
        results = []
        for i, response in enumerate(responses):
            contents = [choice.message.content for choice in response.choices]
            if self.conf.params['n'] == 1:
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
                    sql = self.process_gpt_4o_mini_sql(sql)
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
                final_sqls = await get_sqls([result], self.conf.params['n'],
                                            self.run_conf.dataset_config.get_db_path())
                results.extend(final_sqls)
        return results

    async def ask_file(self, in_path: str, out_path: str) -> GptUsageStats:
        return await self.gpt_sender.send_and_save(in_path, out_path)
