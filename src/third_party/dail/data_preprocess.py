import json
import os
import sys

from tqdm import tqdm

from src.eval.single_run_config import SingleRunConfig
from src.rel.db_factory import DatabaseFactory
from src.sqlyzr.file_gen import FileGenerator
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.db_facade_adapter import DatabaseConnectionProxy
from src.third_party.dail.utils.datasets.spider import load_tables
from src.third_party.dail.utils.linking_process import SpiderEncoderV2Preproc
from src.third_party.dail.utils.pretrained_embeddings import GloVe
from src.util.file_utils import read_json
from src.util.multi_thread_utils import exec_multi_process_chunked

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class DailSchemaLinksGenerator(FileGenerator):
    def __init__(self, dail_conf: DailConfig, run_conf: SingleRunConfig):
        super().__init__(dail_conf.test_schema_path())
        self.dail_conf = dail_conf
        self.run_conf = run_conf

    def _run_internal(self):
        if self.run_conf.dataset_config.dataset_type == "bird":
            bird_pre_process(self.run_conf)

        if self.run_conf.dataset_config.dataset_type == "beaver":
            beaver_pre_process(self.run_conf)

        # load data
        test_data = read_json(self.run_conf.dataset_config.get_test_path())
        train_data = read_json(self.run_conf.dataset_config.get_train_path())

        # load schemas
        schemas, _ = load_tables([self.run_conf.dataset_config.get_tables_path()])

        db_facade = DatabaseFactory.get_instance(self.run_conf.dataset_config)
        for db_id, schema in tqdm(schemas.items(), desc="DB connections"):
            schema.connection = DatabaseConnectionProxy(db_facade, db_id)

        compute_cv_link = self.run_conf.dataset_config.dataset_type == "spider"

        word_emb = GloVe(kind='42B', lemmatize=True)
        linking_processor = SpiderEncoderV2Preproc(min_freq=4,
                                                   max_count=5000,
                                                   include_table_name_in_column=False,
                                                   word_emb=word_emb,
                                                   fix_issue_16_primary_keys=True,
                                                   compute_sc_link=True,
                                                   compute_cv_link=compute_cv_link)
        for data, section in zip([test_data, train_data], ['test', 'train']):
            proc_data_list = []
            for item in tqdm(data, desc=f"{section} section linking"):
                db_id = item["db_id"]
                schema = schemas[db_id]
                proc_data = dict()
                proc_data['item'] = item
                proc_data['schema'] = schema
                linking_processor.preprocess_schema(schema)
                proc_data_list.append(proc_data)
            proc_list = exec_multi_process_chunked(linking_processor.preprocess_items, proc_data_list)

            for proc in proc_list:
                linking_processor.add_proc_item(section, proc)

        linking_processor.save({"train": self.dail_conf.train_schema_path(), "test": self.dail_conf.test_schema_path()})


def beaver_pre_process(run_conf: SingleRunConfig):
    def json_preprocess(data_jsons):
        new_datas = []
        for data_json in data_jsons:
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


def bird_pre_process(run_conf: SingleRunConfig, with_evidence=True):
    def json_preprocess(data_jsons):
        new_datas = []
        for data_json in data_jsons:
            ### Append the evidence to the question
            if with_evidence and len(data_json["evidence"]) > 0:
                if (not 'evidence_added' in data_json) or not data_json['evidence_added']:
                    data_json['question'] = (data_json['question'] + " " + data_json["evidence"]).strip()
                data_json['evidence_added'] = True
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
