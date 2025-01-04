import os
import re
from typing import List, Callable

import pandas as pd

from src.gpt.gpt_from_file_sender import GptFromFileSender, GptBatchSender, GptSingleSender
from src.gpt.gpt_utils import process_responses, load_responses
from src.gpt.models import BatchInputRequest
from src.parse.parser import SqlParser
from src.third_party.din.config import DinConfig
from src.third_party.din.prompt_maker import PromptMaker
from src.util.logger import log

BatchRequestGenerator = Callable[[int, str, str], BatchInputRequest]


def load_data(input_path: str):
    return pd.read_json(input_path)


class DinPredictor:
    conf: DinConfig
    prompt_maker: PromptMaker
    gpt_sender: GptFromFileSender
    schema_links: List[str]
    classifs: List[str]
    pred_classes: List[str]
    sqls: List[str]
    parser: SqlParser
    default_params = {
        'max_completion_tokens': 600,
        'stop': ["Q:"]
    }
    debug_params = {
        "max_completion_tokens": 350,
        "stop": ["#", ";", "\n\n"]
    }

    def __init__(self, conf: DinConfig):
        self.parser = SqlParser()
        self.conf = conf
        if self.conf.run_conf.batch:
            self.gpt_sender = GptBatchSender()
        else:
            self.gpt_sender = GptSingleSender()
        self.prompt_maker = PromptMaker(self.conf.run_conf.dataset_config.get_tables_path())

    def generate_batch_file(self, file_path: str, req_generator: BatchRequestGenerator):
        examples = load_data(self.conf.run_conf.dataset_config.get_data_path()).to_dict("records")
        file = open(file_path, "w")
        for i, example in enumerate(examples):
            db_id = example['db_id']
            question = example['question']
            request = req_generator(i, db_id, question)
            file.write(f"{request.json()}\n")
        file.close()

    async def ask_file(self, in_path: str, out_path: str):
        print(f"Asking GPT {in_path} ==> {out_path}")
        if os.path.exists(out_path) and not self.conf.force:
            log(f"Output path exists: {out_path}, skip asking gpt.")
            return
        await self.gpt_sender.send_and_save(in_path, out_path)

    def create_batch_req(self, idx: str, prompt: str, extra_params):
        extra_params['temperature'] = self.conf.run_conf.temp
        return BatchInputRequest.create_prompt_req(idx, self.conf.model, prompt, extra_params)

    def generate_schema_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        prompt = self.prompt_maker.schema_linking_prompt_maker(question, db_id)
        return self.create_batch_req(f"s{i}", prompt, self.default_params)

    def generate_classif_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        schema_link = self.schema_links[i]
        prompt = self.prompt_maker.classification_prompt_maker(question, db_id, schema_link[1:])
        return self.create_batch_req(f"c{i}", prompt, self.default_params)

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
                print("No sub questions found! :(")
                sub_questions = []
            prompt = self.prompt_maker.hard_prompt_maker(question, db_id, schema_link, sub_questions)
        return self.create_batch_req(f"s{i}", prompt, self.default_params)

    def create_debug_sql_prompt(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        sql = self.sqls[i]
        prompt = self.prompt_maker.debuger(question, db_id, sql)
        return self.create_batch_req(f"sd{i}", prompt, self.debug_params)

    def process_schema_response(self, i: int, content: str) -> str:
        try:
            schema_links = content.split("Schema_links: ")[1]
        except:
            print("Slicing error for the schema_linking module")
            schema_links = "[]"
        return schema_links

    def process_classif_response(self, i: int, content: str) -> str:
        try:
            predicted_class = content.split("Label: ")[1]
        except:
            print("Slicing error for the classification module")
            predicted_class = '"NESTED"'
        return predicted_class

    def process_gpt_4o_mini_sql(self, i: int, content: str) -> str:
        content = content.strip()
        content = content.replace("\n", " ")
        if "SQL: `" in content:
            pattern = r'.*SQL: `\s*(SELECT.*)\s*`'
            content = re.sub(pattern, r'\1', content)
        if "```sql" in content:
            pattern = r'.*```sql\s*(SELECT.*)\s*```'
            content = re.sub(pattern, r'\1', content)
        return content

    def process_gpt_4o_mini_debug(self, content: str) -> str:
        content = content.replace("\n", " ")
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
        match self.conf.model:
            case "gpt-3.5-turbo":
                return self.process_gpt_35_sql(i, content)
            case "gpt-4o-mini":
                return self.process_gpt_4o_mini_sql(i, content)
            case _:
                raise RuntimeError(f"Unknown model: {self.conf.model}")

    def process_sql_debug_response(self, i: int, content: str) -> str:
        match self.conf.model:
            case "gpt-3.5-turbo":
                sql = "SELECT " + content
                return sql
            case "gpt-4o-mini":
                sql = self.process_gpt_4o_mini_debug(content)
                return sql
            case _:
                raise RuntimeError(f"Unknown model: {self.conf.model}")
        # sql = "SELECT " + content
        # pattern = r'SELECT\s*```sql ([^`]*).*'
        # sql = re.sub(pattern, r'\1', sql)
        # return sql

    def post_process(self, sqls: List[str]) -> List[str]:
        result = []
        for sql in sqls:
            sql = sql.replace("\n", " ")
            result.append(sql)
        return result

    def save_sqls(self, out_path, sqls: List[str]):
        file = open(out_path, 'w')
        for sql in sqls:
            file.write(f"{sql}\n")
        file.close()

    def get_token_usage(self, file_path: str):
        token_usage = []
        responses = load_responses(file_path)
        for response in responses:
            token_usage.append(response.usage.total_tokens)
        return token_usage

    def save_total_token_usage(self):
        all_usage = []
        for file in [
            self.conf.get_path("classif", "out"),
            self.conf.get_path("schema", "out"),
            self.conf.get_path("sql", "out"),
            self.conf.get_path("sql_debug", "out")
        ]:
            all_usage.append(self.get_token_usage(file))
        all_usage = [sum(usages) for usages in zip(*all_usage)]
        out_file = open(self.conf.run_conf.get_token_path(), "w")
        for usage in all_usage:
            out_file.write(f"{usage}\n")
        out_file.close()

    async def run(self):
        conf = self.conf

        self.generate_batch_file(conf.get_path("schema", "in"), self.generate_schema_req)

        await self.ask_file(conf.get_path("schema", "in"), conf.get_path("schema", "out"))

        self.schema_links = process_responses(conf.get_path("schema", "out"), self.process_schema_response)

        self.generate_batch_file(conf.get_path("classif", "in"), self.generate_classif_req)

        await self.ask_file(conf.get_path("classif", "in"), conf.get_path("classif", "out"))

        self.classifs = process_responses(conf.get_path("classif", "out"), lambda i, s: s)

        self.pred_classes = process_responses(conf.get_path("classif", "out"), self.process_classif_response)

        self.generate_batch_file(conf.get_path("sql", "in"), self.create_sql_prompt)

        await self.ask_file(conf.get_path("sql", "in"), conf.get_path("sql", "out"))

        self.sqls = process_responses(conf.get_path("sql", "out"), self.process_sql_responses)

        self.generate_batch_file(conf.get_path("sql_debug", "in"), self.create_debug_sql_prompt)

        await self.ask_file(conf.get_path("sql_debug", "in"), conf.get_path("sql_debug", "out"))

        self.sqls = process_responses(conf.get_path("sql_debug", "out"), self.process_sql_debug_response)

        sqls = self.post_process(self.sqls)

        self.save_sqls(self.conf.run_conf.get_pred_path(), sqls)

        self.save_total_token_usage()
