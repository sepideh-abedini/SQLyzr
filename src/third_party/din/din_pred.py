import json
import os
import re
from typing import List, Callable

import pandas as pd

from src.gpt.gpt_utils import process_responses
from src.third_party.din.config import DinConfig, DEFAULT_CONF
from src.gpt.gpt_asker import AsyncGptAsker
from src.third_party.din.prompt_maker import PromptMaker
from src.eval.runner_config import SingleRunConfig
from src.util.logger import log

PromptGenerator = Callable[[int, str, str], str]


def load_data(input_path: str):
    return pd.read_json(input_path)


class DinPredictor:
    conf: DinConfig
    prompt_maker: PromptMaker
    gpt_asker: AsyncGptAsker
    run_conf: SingleRunConfig
    schema_links: List[str]
    classifs: List[str]
    pred_classes: List[str]
    sqls: List[str]
    default_params = {
        'max_tokens': 600,
        'stop': ["Q:"]
    }
    debug_params = {
        "max_tokens": 350,
        "stop": ["#", ";", "\n\n"]
    }

    def __init__(self, run_conf: SingleRunConfig, config: DinConfig = DEFAULT_CONF):
        self.run_conf = run_conf
        self.conf = config
        self.gpt_asker = AsyncGptAsker()
        self.prompt_maker = PromptMaker(run_conf.dataset_config.get_tables_path())

    def generate_messages_file(self, file_path: str, prompt_gen: PromptGenerator):
        examples = load_data(self.run_conf.dataset_config.get_data_path()).to_dict("records")
        file = open(file_path, "w")
        for i, example in enumerate(examples):
            db_id = example['db_id']
            question = example['question']
            content = prompt_gen(i, db_id, question)
            message = {"role": "user", "content": content}
            file.write(f"{json.dumps(message)}\n")
        file.close()

    async def ask_file(self, in_path: str, out_path: str, **kwargs):
        print(f"Asking GPT {in_path} ==> {out_path}")
        if os.path.exists(out_path) and not self.conf.force:
            log(f"Output path exists: {out_path}, skip asking gpt.")
            return
        await self.gpt_asker.ask_file(in_path, out_path, **kwargs)

    def create_schema_link_prompt(self, i: int, db_id: str, question: str) -> str:
        return self.prompt_maker.schema_linking_prompt_maker(question, db_id)

    def create_classif_prompt(self, i: int, db_id: str, question: str) -> str:
        schema_link = self.schema_links[i]
        return self.prompt_maker.classification_prompt_maker(question, db_id, schema_link[1:])

    def create_sql_prompt(self, i: int, db_id: str, question: str) -> str:
        pred_class = self.pred_classes[i]
        classif = self.classifs[i]
        schema_link = self.schema_links[i]
        if '"EASY"' in pred_class:
            content = self.prompt_maker.easy_prompt_maker(question, db_id, schema_link)
        elif '"NON-NESTED"' in pred_class:
            content = self.prompt_maker.medium_prompt_maker(question, db_id, schema_link)
        else:
            if 'questions =[' in classif:
                sub_questions = classif.split('questions = ["')[1].split('"]')[0]
            else:
                print("No sub questions found! :(")
                sub_questions = []
            content = self.prompt_maker.hard_prompt_maker(question, db_id, schema_link, sub_questions)
        return content

    def create_debug_sql_prompt(self, i: int, db_id: str, question: str) -> str:
        sql = self.sqls[i]
        return self.prompt_maker.debuger(question, db_id, sql)

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

    def process_sql_responses(self, i: int, content: str) -> str:
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

    def process_sql_debug_response(self, i: int, content: str) -> str:
        sql = "SELECT " + content
        pattern = r'SELECT\s*```sql ([^`]*).*'
        sql = re.sub(pattern, r'\1', sql)
        return sql

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

    async def run(self):
        conf = self.conf

        self.generate_messages_file(conf.schema_in, self.create_schema_link_prompt)

        await self.ask_file(conf.schema_in, conf.schema_out, **self.default_params)

        self.schema_links = process_responses(conf.schema_out, self.process_schema_response)

        self.generate_messages_file(conf.classif_in, self.create_classif_prompt)

        await self.ask_file(conf.classif_in, conf.classif_out, **self.default_params)

        self.classifs = process_responses(conf.classif_out, lambda i, s: s)

        self.pred_classes = process_responses(conf.classif_out, self.process_classif_response)

        self.generate_messages_file(conf.sql_in, self.create_sql_prompt)

        await self.ask_file(conf.sql_in, conf.sql_out, **self.default_params)

        self.sqls = process_responses(conf.sql_out, self.process_sql_responses)

        self.generate_messages_file(conf.sql_debug_in, self.create_debug_sql_prompt)

        await self.ask_file(conf.sql_debug_in, conf.sql_debug_out, **self.debug_params)

        self.sqls = process_responses(conf.sql_debug_out, self.process_sql_debug_response)

        sqls = self.post_process(self.sqls)

        self.save_sqls(self.run_conf.get_pred_path(), sqls)
