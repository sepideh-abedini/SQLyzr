import json
import os
import random
from typing import List, Dict, Set

import tqdm

from src.aug.aug_out import AugOut
from src.aug.auger_conf import AugerConf, DEFAULT_CONF
from src.aug.prompt import GptPromptSubCat
from src.aug.text_sql_pair import TextSqlPair
from src.aug.text_sql_pair_example import TextSqlPairExample
from src.cat.catter import Catter
from src.cat.sub_category import SubCategory
from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.dataset_config import DatasetConfig
from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.file_sender.formatted_sender import GptFormattedSingleSender
from src.gpt.models import BatchInputRequest
from src.pred.predictor import process_formatted_responses
from src.util.log_util import log
from src.util.model_utils import write_jsonl
from src.util.schema_repo import DatabaseSchemaRepo

from loguru import logger


class Auger:
    __gpt_sender: GptFileSender
    __conf: AugerConf
    __dataset_conf: DatasetConfig
    __examples: Dict[SubCategory, List[TextSqlPairExample]]
    __sub_cats: Set[SubCategory]
    __db_id: str
    __catter: Catter
    __sqlyzr_conf: SQLyzrConfig

    def __init__(self, sqlyzr_config: SQLyzrConfig, ds_conf: DatasetConfig, sub_cats: Set[SubCategory],
                 db_id: str = None,
                 conf=DEFAULT_CONF):
        self.__sqlyzr_conf = sqlyzr_config
        self.__dataset_conf = ds_conf
        self.__conf = AugerConf(os.path.join(sqlyzr_config.aug_dir, ds_conf.dataset_type))
        self.__sub_cats = sub_cats
        self.__catter = Catter()
        self.__gpt_sender = GptFormattedSingleSender(TextSqlPair)
        self.schema_repo = DatabaseSchemaRepo(self.__dataset_conf.get_tables_path())
        if db_id:
            self.__db_id = db_id
        else:
            self.__db_id = self.schema_repo.get_db_id_with_most_columns()
        self.__examples = self.__extract_examples(self.__dataset_conf)
        os.makedirs(self.__conf.aug_dir, exist_ok=True)

    async def run(self):
        conf = self.__conf
        self.__gen_batch_file(conf.get_aug_in())
        await self.__ask_file(conf.get_aug_in(), conf.get_aug_out())

        resps = process_formatted_responses(conf.get_aug_out(), TextSqlPair, self.__process_response)
        write_jsonl(resps, conf.get_aug_res())

    @log("Extracting examples")
    def __extract_examples(self, ds_conf: DatasetConfig):
        examples = {}
        with open(ds_conf.get_test_path()) as dataset_file:
            dataset_data = json.load(dataset_file)
            for entry in tqdm.tqdm(dataset_data, desc="Extracting examples", total=len(dataset_data)):
                db_id = entry["db_id"]
                sql = entry["query"]
                sub = self.__catter.get_sub_category(sql)
                schema = self.schema_repo.dbs[db_id]
                ex = TextSqlPairExample(sql=sql, question=entry["question"], schema=schema)
                examples.setdefault(sub, []).append(ex)
        return examples

    def __get_prompt_for_sub_cat(self, cat: SubCategory) -> GptPromptSubCat:
        sub_cat_examples = []
        if cat in self.__examples:
            all_examples = self.__examples[cat]
            sub_cat_examples = random.sample(all_examples, min(len(all_examples), self.__conf.num_examples))
        prompt = GptPromptSubCat(schema=self.schema_repo.dbs[self.__db_id], cat=cat, examples=sub_cat_examples)
        return prompt

    def __create_batch_req(self, idx: str, prompt: str, extra_params):
        return

    def __gen_batch_file(self, file_path: str):
        file = open(file_path, "w")
        for sub_cat in self.__sub_cats:
            for i in range(self.__sqlyzr_conf.aug_per_sub_cat):
                prompt = self.__get_prompt_for_sub_cat(sub_cat)
                request = BatchInputRequest.create_prompt_req(f"a{i}", str(prompt), self.__conf.gpt_params)
                file.write(f"{request.json()}\n")
        file.close()

    @log("Asking GPT")
    async def __ask_file(self, in_path: str, out_path: str):
        if os.path.exists(out_path):
            logger.debug(f"Output path exists: {out_path}, skip asking gpt.")
            return
        await self.__gpt_sender.send_and_save(in_path, out_path)

    def __process_response(self, i: int, pair: TextSqlPair) -> AugOut:
        d = pair.dict()
        d['db_id'] = self.__db_id
        d['sub_cat'] = str(self.__catter.get_sub_category(pair.sql))
        return AugOut.model_validate(d)
