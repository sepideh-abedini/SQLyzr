import json
import os
import random
from typing import List, Dict

import tqdm
from pydantic import BaseModel

from src.aug.auger_conf import AugerConf, DEFAULT_CONF
from src.aug.prompt import GptPromptSubCat
from src.aug.text_sql_pair_example import TextSqlPairExample
from src.cat.catter import Catter
from src.cat.statement_category import StatementCategory
from src.cat.sub_category import SubCategory
from src.configs.sqlyzr import SQLyzrConfig
from src.eval.dataset_config import DatasetConfig
from src.gpt.gpt_from_file_sender import GptFormattedSingleSender, GptFromFileSender
from src.gpt.gpt_utils import process_formatted_responses
from src.gpt.models import BatchInputRequest
from src.util.logger import log, debug_log
from src.util.schema_repo import DatabaseSchemaRepo


class TextSqlPair(BaseModel):
    sql: str
    question: str


class Auger:
    gpt_sender: GptFromFileSender
    conf: AugerConf
    dataset_conf: DatasetConfig
    force: bool = False
    out: str
    examples: Dict[SubCategory, List[TextSqlPairExample]]
    sub_cats: List[SubCategory]
    db_id: str
    catter: Catter

    def __init__(self, sqlyzr_config: SQLyzrConfig, sub_cats: List[SubCategory], conf=DEFAULT_CONF):
        self.out = sqlyzr_config.get_aug_out()
        self.sqlyzr_conf = sqlyzr_config
        self.conf = AugerConf(sqlyzr_config.aug_dir)
        self.sub_cats = sub_cats
        self.catter = Catter()
        self.gpt_sender = GptFormattedSingleSender(TextSqlPair)
        self.schema_repo = DatabaseSchemaRepo(self.sqlyzr_conf.eval_conf.dataset_config.get_tables_path())
        self.db_id = self.schema_repo.get_db_id_with_most_columns()
        self.examples = self.extract_examples()

    def extract_examples(self):
        examples = {}
        with open(self.sqlyzr_conf.eval_conf.dataset_config.get_data_path()) as dataset_file:
            dataset_data = json.load(dataset_file)
            for entry in tqdm.tqdm(dataset_data, total=len(dataset_data)):
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
        for sub_cat in self.sub_cats:
            for i in range(self.sqlyzr_conf.aug_per_sub_cat):
                prompt = self.get_gen_prompt_for_sub_cat(sub_cat)
                request = self.create_batch_req(f"a{i}", str(prompt), dict())
                file.write(f"{request.json()}\n")
        file.close()

    async def ask_file(self, in_path: str, out_path: str):
        debug_log(f"Asking GPT {in_path} ==> {out_path}")
        if os.path.exists(out_path) and not self.force:
            debug_log(f"Output path exists: {out_path}, skip asking gpt.")
            return
        await self.gpt_sender.send_and_save(in_path, out_path)

    def process_response(self, i: int, pair: TextSqlPair) -> Dict:
        d = pair.dict()
        d['db_id'] = self.db_id
        d['sub_cat'] = str(self.catter.get_sub_category(pair.sql))
        return d

    def save_results(self, dicts: List[Dict]):
        file = open(self.out, "w")
        for d in dicts:
            file.write(f"{json.dumps(d)}\n")

    async def run(self):
        conf = self.conf
        self.generate_batch_file(conf.get_aug_in())
        await self.ask_file(conf.get_aug_in(), conf.get_aug_out())
        resps = process_formatted_responses(conf.get_aug_out(), TextSqlPair, self.process_response)
        self.save_results(resps)
