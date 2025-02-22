import json
import os

from src.eval.dataset_config import DatasetConfig
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.utils.utils import get_tables, sql2skeleton
from src.third_party.dail.utils.linking_utils.application import get_question_pattern_with_schema_linking
from src.util.file_utils import read_json


class BasicDataset:
    config: DatasetConfig
    dail_conf: DailConfig
    databases = None

    def __init__(self, config: DatasetConfig, dail_conf: DailConfig):
        self.config = config
        self.dail_conf = dail_conf

    def get_databases(self):
        if self.databases is None:
            self.databases = dict()
            # for db_id in os.listdir(self.path_db):
            #     self.databases[db_id] = self.get_tables(db_id)
            with open(self.config.get_tables_path()) as f:
                tables = json.load(f)
                for tj in tables:
                    db_id = tj["db_id"]
                    self.databases[db_id] = self.get_tables(db_id)
        return self.databases

    def get_tables(self, db_id):
        if db_id in self.databases:
            return self.databases[db_id]
        else:
            path_db = self.config.get_db_file_path(db_id)
            tables = get_tables(path_db)
            self.databases[db_id] = tables
            return tables

    def get_train_json(self):
        datas = read_json(self.config.get_train_path())
        linking_infos = self.get_train_schema_linking()
        db_id_to_table_json = dict()
        for table_json in self.get_table_json():
            db_id_to_table_json[table_json["db_id"]] = table_json
        schemas = [db_id_to_table_json[d["db_id"]] for d in datas]
        queries = [data["query"] for data in datas]
        pre_queries = self.get_pre_skeleton(queries, schemas)
        return self.data_pre_process(datas, linking_infos, pre_queries)

    def get_test_schema_linking(self):
        if not os.path.exists(self.dail_conf.test_schema_path()):
            return None
        linking_infos = []
        with open(self.dail_conf.test_schema_path(), 'r') as f:
            for line in f.readlines():
                if line.strip():
                    linking_infos.append(json.loads(line))
        return linking_infos

    def get_test_json(self, mini_set=False):
        tests = read_json(self.config.get_test_path())
        linking_infos = self.get_test_schema_linking()
        db_id_to_table_json = dict()
        for table_json in self.get_table_json():
            db_id_to_table_json[table_json["db_id"]] = table_json
        schemas = [db_id_to_table_json[d["db_id"]] for d in tests]

        if os.path.exists(self.dail_conf.pre_test_result_path()):
            with open(self.dail_conf.pre_test_result_path(), 'r') as f:
                lines = f.readlines()
                queries = [line.strip() for line in lines]
                pre_queries = self.get_pre_skeleton(queries, schemas)
        else:
            pre_queries = None
        return self.data_pre_process(tests, linking_infos, pre_queries)

    def get_train_schema_linking(self):
        if not os.path.exists(self.dail_conf.train_schema_path()):
            return None
        linking_infos = []
        with open(self.dail_conf.train_schema_path(), 'r') as f:
            for line in f.readlines():
                if line.strip():
                    linking_infos.append(json.loads(line))
        return linking_infos

    def get_table_json(self):
        return read_json(self.config.get_tables_path())

    def get_pre_skeleton(self, queries=None, schemas=None):
        if queries:
            skeletons = []
            for query, schema in zip(queries, schemas):
                skeletons.append(sql2skeleton(query, schema))
            return skeletons
        else:
            return False

    def data_pre_process(self, datas, linking_infos=None, pre_queries=None):
        db_id_to_table_json = dict()
        for table_json in self.get_table_json():
            db_id_to_table_json[table_json["db_id"]] = table_json
        for data in datas:
            db_id = data["db_id"]
            data["tables"] = self.get_tables(db_id)
            if data["query"].strip()[:6] != 'SELECT':
                data["query_skeleton"] = data["query"]
            else:
                data["query_skeleton"] = sql2skeleton(data["query"], db_id_to_table_json[db_id])
            data["path_db"] = self.get_path_db(db_id)
        if linking_infos:
            db_id_to_table_json = dict()
            for table_json in self.get_table_json():
                db_id_to_table_json[table_json["db_id"]] = table_json
            for id in range(min(len(datas), len(linking_infos))):
                datas[id]["sc_link"] = linking_infos[id]["sc_link"]
                datas[id]["cv_link"] = linking_infos[id]["cv_link"]
                datas[id]["question_for_copying"] = linking_infos[id]["question_for_copying"]
                datas[id]["column_to_table"] = linking_infos[id]["column_to_table"]
                db_id = datas[id]["db_id"]
                datas[id]["table_names_original"] = db_id_to_table_json[db_id]["table_names_original"]
            question_patterns = get_question_pattern_with_schema_linking(datas)
            for id in range(len(datas)):
                datas[id]["question_pattern"] = question_patterns[id]
        if pre_queries:
            for id in range(min(len(datas), len(pre_queries))):
                datas[id]["pre_skeleton"] = pre_queries[id]
        return datas

    def get_path_db(self, db_id):
        return self.config.get_db_file_path(db_id)

    def get_train_questions(self):
        questions = read_json(self.config.get_train_path())
        return [_["question"] for _ in questions]


def load_data(config: DatasetConfig, dail_conf: DailConfig):
    if config.dataset_type.lower() == "spider" or config.dataset_type.lower() == 'bird':
        return BasicDataset(config, dail_conf)
    else:
        raise RuntimeError()
