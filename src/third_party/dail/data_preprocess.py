import json
import os
import sqlite3
from pathlib import Path

from tqdm import tqdm

from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.file_gen import FileGenerator
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.utils.datasets.spider import load_tables
from src.third_party.dail.utils.linking_process import SpiderEncoderV2Preproc
from src.third_party.dail.utils.pretrained_embeddings import GloVe
from src.util.file_utils import read_json

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class DailSchemaLinksGenerator(FileGenerator):
    def __init__(self, dail_conf: DailConfig, run_conf: SingleRunConfig):
        super().__init__(dail_conf.test_schema_path())
        self.dail_conf = dail_conf
        self.run_conf = run_conf

    def _run_internal(self):
        if self.run_conf.dataset_config.dataset_type == "bird":
            bird_pre_process(self.run_conf)

        # load data
        test_data = read_json(self.run_conf.dataset_config.get_test_path())
        train_data = read_json(self.run_conf.dataset_config.get_train_path())

        # load schemas
        schemas, _ = load_tables([self.run_conf.dataset_config.get_tables_path()])

        # Backup in-memory copies of all the DBs and create the live connections
        for db_id, schema in tqdm(schemas.items(), desc="DB connections"):
            sqlite_path = self.run_conf.dataset_config.get_db_file_path(db_id)
            source: sqlite3.Connection
            with sqlite3.connect(str(sqlite_path)) as source:
                dest = sqlite3.connect(':memory:')
                dest.row_factory = sqlite3.Row
                source.backup(dest)
            schema.connection = dest

        word_emb = GloVe(kind='42B', lemmatize=True)
        linking_processor = SpiderEncoderV2Preproc(min_freq=4,
                                                   max_count=5000,
                                                   include_table_name_in_column=False,
                                                   word_emb=word_emb,
                                                   fix_issue_16_primary_keys=True,
                                                   compute_sc_link=True,
                                                   compute_cv_link=True)

        # build schema-linking
        for data, section in zip([test_data, train_data], ['test', 'train']):
            for item in tqdm(data, desc=f"{section} section linking"):
                db_id = item["db_id"]
                schema = schemas[db_id]
                to_add, validation_info = linking_processor.validate_item(item, schema, section)
                if to_add:
                    linking_processor.add_item(item, schema, section, validation_info)

        # save
        linking_processor.save({"train": self.dail_conf.train_schema_path(), "test": self.dail_conf.test_schema_path()})


def bird_pre_process(run_conf: SingleRunConfig, with_evidence=True):
    def json_preprocess(data_jsons):
        new_datas = []
        for data_json in data_jsons:
            ### Append the evidence to the question
            if with_evidence and len(data_json["evidence"]) > 0:
                data_json['question'] = (data_json['question'] + " " + data_json["evidence"]).strip()
            question = data_json['question']
            tokens = []
            for token in question.split(' '):
                if len(token) == 0:
                    continue
                if token[-1] in ['?', '.', ':', ';', ','] and len(token) > 1:
                    tokens.extend([token[:-1], token[-1:]])
                else:
                    tokens.append(token)
            data_json['question_toks'] = tokens
            data_json['query'] = data_json['SQL']
            new_datas.append(data_json)
        return new_datas

    with open(run_conf.dataset_config.get_test_path()) as f:
        data_jsons = json.load(f)
    with open(run_conf.dataset_config.get_test_path(), 'w') as wf:
        json.dump(json_preprocess(data_jsons), wf, indent=4)

    with open(run_conf.dataset_config.get_train_path()) as f:
        data_jsons = json.load(f)
    with open(run_conf.dataset_config.get_train_path(), 'w') as wf:
        json.dump(json_preprocess(data_jsons), wf, indent=4)
