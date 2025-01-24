import json
import re
from abc import ABC
from typing import List, Callable

import pandas as pd

from src.eval.single_run_config import SingleRunConfig
from src.gpt.gpt_from_file_sender import GptFromFileSender, GptBatchSender, GptSingleSender
from src.gpt.gpt_usage_stats import GptUsageStats
from src.gpt.models import BatchInputRequest
from src.gpt.utils import process_responses, load_responses
from src.parse.parser import SqlParser
from src.third_party.din.config import DinConfig
from src.third_party.din.prompt_maker import PromptMaker
from src.third_party.model_stats import ModelRunStats

BatchRequestGenerator = Callable[[int, str, str], BatchInputRequest]


def load_data(input_path: str):
    return pd.read_json(input_path)


class Predictor(ABC):
    run_conf: SingleRunConfig

    def __init__(self, run_conf: SingleRunConfig):
        self.run_conf = run_conf
        self.parser = SqlParser()
        if self.run_conf.batch:
            self.gpt_sender = GptBatchSender()
        else:
            self.gpt_sender = GptSingleSender()

    async def ask_file(self, in_path: str, out_path: str):
        return await self.gpt_sender.send_and_save(in_path, out_path)

    def gen_batch_file(self, file_path: str, gen_req: BatchRequestGenerator):
        examples = load_data(self.run_conf.dataset_config.get_data_path()).to_dict("records")
        file = open(file_path, "w")
        for i, example in enumerate(examples):
            db_id = example['db_id']
            question = example['question']
            request = gen_req(i, db_id, question)
            file.write(f"{request.json()}\n")
        file.close()

    def create_batch_req(self, idx: str, prompt: str, extra_params):
        extra_params['temperature'] = self.run_conf.temp
        return BatchInputRequest.create_prompt_req(idx, prompt, extra_params)


class DinPredictor(Predictor):
    conf: DinConfig
    run_conf: SingleRunConfig
    prompt_maker: PromptMaker
    gpt_sender: GptFromFileSender
    schema_links: List[str]
    classifs: List[str]
    pred_classes: List[str]
    sqls: List[str]
    parser: SqlParser
    stats: ModelRunStats

    def __init__(self, run_conf: SingleRunConfig):
        super().__init__(run_conf)
        self.conf = DinConfig(run_conf.get_pred_path())
        self.prompt_maker = PromptMaker(self.run_conf.dataset_config.get_tables_path())
        self.stats = ModelRunStats()

    def generate_schema_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        prompt = self.prompt_maker.schema_linking_prompt_maker(question, db_id)
        return self.create_batch_req(f"s{i}", prompt, self.conf.default_params)

    def generate_classif_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        schema_link = self.schema_links[i]
        prompt = self.prompt_maker.classification_prompt_maker(question, db_id, schema_link[1:])
        return self.create_batch_req(f"c{i}", prompt, self.conf.default_params)

    def create_sql_prompt(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        pred_class = self.pred_classes[i]
        classif = self.classifs[i]
        schema_link = self.schema_links[i]
        if '"EASY"' in pred_class:
            prompt = self.prompt_maker.easy_prompt_maker(question, db_id, schema_link)
        elif '"NON-NESTED"' in pred_class:
            prompt = self.prompt_maker.medium_prompt_maker(question, db_id, schema_link)
        else:
            if 'questions =[' in classif:
                sub_questions = classif.split('questions = ["')[1].split('"]')[0]
            else:
                # print("No sub questions found! :(")
                sub_questions = []
            prompt = self.prompt_maker.hard_prompt_maker(question, db_id, schema_link, sub_questions)
        return self.create_batch_req(f"s{i}", prompt, self.conf.default_params)

    def create_debug_sql_prompt(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        sql = self.sqls[i]
        prompt = self.prompt_maker.debuger(question, db_id, sql)
        return self.create_batch_req(f"sd{i}", prompt, self.conf.debug_params)

    @staticmethod
    def process_schema_response(i: int, content: str) -> str:
        try:
            schema_links = content.split("Schema_links: ")[1]
        except:
            print("Slicing error for the schema_linking module")
            schema_links = "[]"
        return schema_links

    @staticmethod
    def process_classif_response(i: int, content: str) -> str:
        try:
            predicted_class = content.split("Label: ")[1]
        except:
            print("Slicing error for the classification module")
            predicted_class = '"NESTED"'
        return predicted_class

    @staticmethod
    def process_gpt_4o_mini_sql(i: int, content: str) -> str:
        content = content.strip()
        content = content.replace("\n", " ")
        if "SQL:" in content:
            pattern = r'.*SQL:[\s`]*(SELECT.*)[\s`]*'
            content = re.sub(pattern, r'\1', content)
        if "```sql" in content:
            pattern = r'.*```sql\s*(SELECT.*)\s*```'
            content = re.sub(pattern, r'\1', content)
        return content

    def process_gpt_4o_mini_debug(self, i: int, content: str) -> str:
        content = content.replace("\n", " ")
        if "SELECT" not in content:
            return self.sqls[i]
        pattern = r'.*```sql\s*([^`]*).*'
        sql = re.sub(pattern, r'\1', content)
        sql = sql.strip()
        return sql

    def process_gpt_35_sql(self, i: int, content: str) -> str:
        pred_class = self.pred_classes[i]
        if '"EASY"' in pred_class:
            sql = content
        elif '"NON-NESTED"' in pred_class:
            try:
                sql = content.split("SQL: ")[1]
            except:
                print("SQL slicing error")
                sql = "SELECT"
        else:
            try:
                sql = content.split("SQL: ")[1]
            except:
                print("SQL slicing error")
                sql = "SELECT"
        return sql

    def process_sql_responses(self, i: int, content: str) -> str:
        match self.conf.default_params['model']:
            case "gpt-3.5-turbo":
                return self.process_gpt_35_sql(i, content)
            case "gpt-4o-mini":
                return self.process_gpt_4o_mini_sql(i, content)
            case _:
                raise RuntimeError(f"Unknown model: {self.conf.default_params['model']}")

    def process_sql_debug_response(self, i: int, content: str) -> str:
        match self.conf.default_params['model']:
            case "gpt-3.5-turbo":
                sql = "SELECT " + content
                return sql
            case "gpt-4o-mini":
                sql = self.process_gpt_4o_mini_debug(i, content)
                return sql
            case _:
                raise RuntimeError(f"Unknown model: {self.conf.default_params['model']}")
        # sql = "SELECT " + content
        # pattern = r'SELECT\s*```sql ([^`]*).*'
        # sql = re.sub(pattern, r'\1', sql)
        # return sql

    @staticmethod
    def post_process(sqls: List[str]) -> List[str]:
        result = []
        for sql in sqls:
            sql = sql.replace("\n", " ")
            result.append(sql)
        return result

    @staticmethod
    def save_sqls(out_path, sqls: List[str]):
        file = open(out_path, 'w')
        for sql in sqls:
            file.write(f"{sql}\n")
        file.close()

    async def run(self):
        conf = self.conf

        self.gen_batch_file(conf.get_path("schema", "in"), self.generate_schema_req)

        await self.ask_file(conf.get_path("schema", "in"), conf.get_path("schema", "out"))

        self.schema_links = process_responses(conf.get_path("schema", "out"), self.process_schema_response)

        self.gen_batch_file(conf.get_path("classif", "in"), self.generate_classif_req)

        await self.ask_file(conf.get_path("classif", "in"), conf.get_path("classif", "out"))

        self.classifs = process_responses(conf.get_path("classif", "out"), lambda i, s: s)

        self.pred_classes = process_responses(conf.get_path("classif", "out"), self.process_classif_response)

        self.gen_batch_file(conf.get_path("sql", "in"), self.create_sql_prompt)

        await self.ask_file(conf.get_path("sql", "in"), conf.get_path("sql", "out"))

        self.sqls = process_responses(conf.get_path("sql", "out"), self.process_sql_responses)

        self.gen_batch_file(conf.get_path("sql_debug", "in"), self.create_debug_sql_prompt)

        await self.ask_file(conf.get_path("sql_debug", "in"), conf.get_path("sql_debug", "out"))

        self.sqls = process_responses(conf.get_path("sql_debug", "out"), self.process_sql_debug_response)

        sqls = self.post_process(self.sqls)

        self.save_sqls(self.run_conf.get_pred_path(), sqls)
