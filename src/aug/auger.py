import json
import os
import random
from typing import List, Dict

from pydantic import BaseModel

from src.aug.auger_conf import AugerConf, DEFAULT_CONF
from src.aug.prompt import GptPromptSubCat
from src.aug.text_sql_pair_example import TextSqlPairExample
from src.cat.catter import Catter
from src.cat.statement_category import StatementCategory
from src.cat.sub_category import SubCategory
from src.eval.dataset_config import DatasetConfig
from src.gpt.gpt_asker import AsyncGptAsker, AsyncGptFormattedAsker
from src.gpt.gpt_utils import process_responses, process_formatted_responses
from src.gpt.models import BatchInputRequest
from src.util.logger import log
from src.util.schema_repo import DatabaseSchemaRepo


class TextSqlPair(BaseModel):
    sql: str
    question: str


class Auger:
    gpt_asker: AsyncGptAsker
    conf: AugerConf
    dataset_conf: DatasetConfig
    force: bool = False
    out: str
    examples: Dict[SubCategory, List[TextSqlPairExample]]
    sub_cats: List[SubCategory]
    db_id: str
    catter: Catter

    def __init__(self, out, cat: StatementCategory, db_id: str, dataset_conf: DatasetConfig, conf=DEFAULT_CONF):
        self.out = out
        self.db_id = db_id
        self.conf = conf
        self.sub_cats = []
        self.catter = Catter()
        self.dataset_conf = dataset_conf
        self.gpt_asker = AsyncGptFormattedAsker(TextSqlPair)
        self.schema_repo = DatabaseSchemaRepo(self.dataset_conf.get_tables_path())
        self.examples = self.extract_examples()
        for s in cat.sub_cats:
            if s in self.examples.keys():
                self.sub_cats.append(s)
        log(f"Generating for sub_cats: {self.sub_cats}")

    def extract_examples(self):
        examples = {}
        with open(self.dataset_conf.get_data_path()) as dataset_file:
            dataset_data = json.load(dataset_file)
            for entry in dataset_data:
                db_id = entry["db_id"]
                sql = entry["query"]
                root_cat = self.catter.get_category(sql)
                cat = self.catter.get_sub_category(sql)
                schema = self.schema_repo.dbs[db_id]
                ex = TextSqlPairExample(sql=sql, question=entry["question"], schema=schema)
                examples.setdefault(cat, []).append(ex)
        return examples

    def get_gen_prompt_for_sub_cat(self, cat: SubCategory) -> GptPromptSubCat:
        sub_cat_examples = []
        if cat in self.examples:
            all_examples = self.examples[cat]
            sub_cat_examples = random.sample(all_examples, min(len(all_examples), self.conf.num_examples))
        prompt = GptPromptSubCat(schema=self.schema_repo.dbs[self.db_id], cat=cat, examples=sub_cat_examples)
        return prompt

    def create_batch_req(self, idx: str, prompt: str, extra_params):
        return BatchInputRequest.create_prompt_req(idx, self.conf.model, prompt, extra_params)

    def generate_batch_file(self, file_path: str):
        file = open(file_path, "w")
        for i in range(self.conf.gen_num):
            sub_cat = random.choice(list(self.sub_cats))
            prompt = self.get_gen_prompt_for_sub_cat(sub_cat)
            request = self.create_batch_req(f"a{i}", str(prompt), dict())
            file.write(f"{request.json()}\n")
        file.close()

    async def ask_file(self, in_path: str, out_path: str):
        print(f"Asking GPT {in_path} ==> {out_path}")
        if os.path.exists(out_path) and not self.force:
            log(f"Output path exists: {out_path}, skip asking gpt.")
            return
        await self.gpt_asker.ask_file(in_path, out_path)

    def process_response(self, i: int, pair: TextSqlPair) -> Dict:
        d = pair.dict()
        d['db_id'] = self.db_id
        d['cat'] = str(self.catter.get_category(pair.sql))
        return d

    def save_results(self, dicts: List[Dict]):
        file = open(self.out, "w")
        for d in dicts:
            file.write(f"{json.dumps(d)}\n")

    async def run(self):
        conf = self.conf
        self.generate_batch_file(conf.gen_in)
        await self.ask_file(conf.gen_in, conf.gen_out)
        resps = process_formatted_responses(conf.gen_out, TextSqlPair, self.process_response)
        self.save_results(resps)
