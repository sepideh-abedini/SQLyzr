import json
import os
import sqlite3

from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.file_gen import FileGenerator
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.utils.datasets.spider import load_tables
from src.third_party.dail.utils.linking_process import SpiderEncoderV2Preproc
from src.third_party.dail.utils.pretrained_embeddings import GloVe

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class DailSchemaLinksGenerator(FileGenerator):
    def __init__(self, dail_conf: DailConfig, run_conf: SingleRunConfig):
        super().__init__(dail_conf.schema_path())
        self.dail_conf = dail_conf
        self.run_conf = run_conf

    def _run_internal(self):
        dail_conf = self.dail_conf
        run_conf = self.run_conf

        if run_conf.dataset_config.dataset_type == 'bird':
            bird_pre_process(run_conf)

        # load data
        input_data = json.load(open(run_conf.dataset_config.get_test_path()))
        # load schemas
        schemas, _ = load_tables([run_conf.dataset_config.get_tables_path()])

        # Backup in-memory copies of all the DBs and create the live connections
        for db_id, schema in schemas.items():
            sqlite_path = os.path.join(run_conf.dataset_config.get_db_file_path(db_id))
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
                                                   compute_cv_link=dail_conf.compute_cv_link)

        # build schema-linking
        section = "train"
        for item in input_data:
            db_id = item["db_id"]
            schema = schemas[db_id]
            to_add, validation_info = linking_processor.validate_item(item, schema, section)
            if to_add:
                linking_processor.add_item(item, schema, section, validation_info)

        # save
        linking_processor.save(dail_conf.schema_path(), section)


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
