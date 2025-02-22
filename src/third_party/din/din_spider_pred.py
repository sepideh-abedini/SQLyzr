import re
from typing import List

from src.eval.single_run_config import SingleRunConfig
from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.models import BatchInputRequest
from src.parse.parser import SqlParser
from src.pred.predictor import Predictor, process_responses
from src.third_party.din.config import DinConfig
from src.third_party.din.spider.prompt_maker import PromptMaker


class DinPredictor(Predictor):
    __conf: DinConfig
    __prompt_maker: PromptMaker
    __gpt_sender: GptFileSender
    __schema_links: List[str]
    __classifs: List[str]
    __pred_classes: List[str]
    __sqls: List[str]
    __parser: SqlParser

    def __init__(self, run_conf: SingleRunConfig):
        super().__init__(run_conf)
        self.__conf = DinConfig(run_conf.get_pred_path())
        self.__prompt_maker = PromptMaker(self._run_conf.dataset_config.get_tables_path())

    async def _run_internal(self):
        conf = self.__conf

        self._gen_batch_file(conf.get_path("schema", "in"), self.__generate_schema_req)

        await self._ask_file(conf.get_path("schema", "in"), conf.get_path("schema", "out"))

        self.__schema_links = process_responses(conf.get_path("schema", "out"), self.__process_schema_response)

        self._gen_batch_file(conf.get_path("classif", "in"), self.__generate_classif_req)

        await self._ask_file(conf.get_path("classif", "in"), conf.get_path("classif", "out"))

        self.__classifs = process_responses(conf.get_path("classif", "out"), lambda i, s: s)

        self.__pred_classes = process_responses(conf.get_path("classif", "out"), self.__process_classif_response)

        self._gen_batch_file(conf.get_path("sql", "in"), self.__create_sql_prompt)

        await self._ask_file(conf.get_path("sql", "in"), conf.get_path("sql", "out"))

        self.__sqls = process_responses(conf.get_path("sql", "out"), self.__process_sql_responses)

        self._gen_batch_file(conf.get_path("sql_debug", "in"), self.__create_debug_sql_prompt)

        await self._ask_file(conf.get_path("sql_debug", "in"), conf.get_path("sql_debug", "out"))

        self.__sqls = process_responses(conf.get_path("sql_debug", "out"), self.__process_sql_debug_response)

        sqls = self.__post_process(self.__sqls)

        self._save_sqls(sqls)

    def __generate_schema_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        prompt = self.__prompt_maker.schema_linking_prompt_maker(question, db_id)
        return self._create_batch_req(f"s{i}", prompt, self.__conf.default_params)

    def __generate_classif_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        schema_link = self.__schema_links[i]
        prompt = self.__prompt_maker.classification_prompt_maker(question, db_id, schema_link[1:])
        return self._create_batch_req(f"c{i}", prompt, self.__conf.default_params)

    def __create_sql_prompt(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        pred_class = self.__pred_classes[i]
        classif = self.__classifs[i]
        schema_link = self.__schema_links[i]
        if '"EASY"' in pred_class:
            prompt = self.__prompt_maker.easy_prompt_maker(question, db_id, schema_link)
        elif '"NON-NESTED"' in pred_class:
            prompt = self.__prompt_maker.medium_prompt_maker(question, db_id, schema_link)
        else:
            if 'questions =[' in classif:
                sub_questions = classif.split('questions = ["')[1].split('"]')[0]
            else:
                # print("No sub questions found! :(")
                sub_questions = []
            prompt = self.__prompt_maker.hard_prompt_maker(question, db_id, schema_link, sub_questions)
        return self._create_batch_req(f"s{i}", prompt, self.__conf.default_params)

    def __create_debug_sql_prompt(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        sql = self.__sqls[i]
        prompt = self.__prompt_maker.debuger(question, db_id, sql)
        return self._create_batch_req(f"sd{i}", prompt, self.__conf.debug_params)

    @staticmethod
    def __process_schema_response(i: int, content: str) -> str:
        try:
            schema_links = content.split("Schema_links: ")[1]
        except:
            print("Slicing error for the schema_linking module")
            schema_links = "[]"
        return schema_links

    @staticmethod
    def __process_classif_response(i: int, content: str) -> str:
        try:
            predicted_class = content.split("Label: ")[1]
        except:
            print("Slicing error for the classification module")
            predicted_class = '"NESTED"'
        return predicted_class

    @staticmethod
    def __process_gpt_4o_mini_sql(i: int, content: str) -> str:
        content = content.strip()
        content = content.replace("\n", " ")
        if "SQL:" in content:
            pattern = r'.*SQL:[\s`]*(SELECT.*)[\s`]*'
            content = re.sub(pattern, r'\1', content)
        if "```sql" in content:
            pattern = r'.*```sql\s*(SELECT.*)\s*```'
            content = re.sub(pattern, r'\1', content)
        return content

    def __process_gpt_4o_mini_debug(self, i: int, content: str) -> str:
        content = content.replace("\n", " ")
        content = content.strip()
        if not content.startswith("SELECT"):
            return self.__sqls[i]
        pattern = r'.*```sql\s*([^`]*).*'
        sql = re.sub(pattern, r'\1', content)
        sql = sql.strip()
        return sql

    def __process_gpt_35_sql(self, i: int, content: str) -> str:
        pred_class = self.__pred_classes[i]
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

    def __process_sql_responses(self, i: int, content: str) -> str:
        match self.__conf.default_params['model']:
            case "gpt-3.5-turbo":
                return self.__process_gpt_35_sql(i, content)
            case "gpt-4o-mini":
                return self.__process_gpt_4o_mini_sql(i, content)
            case _:
                raise RuntimeError(f"Unknown model: {self.__conf.default_params['model']}")

    def __process_sql_debug_response(self, i: int, content: str) -> str:
        match self.__conf.default_params['model']:
            case "gpt-3.5-turbo":
                sql = "SELECT " + content
                return sql
            case "gpt-4o-mini":
                sql = self.__process_gpt_4o_mini_debug(i, content)
                return sql
            case _:
                raise RuntimeError(f"Unknown model: {self.__conf.default_params['model']}")
        # sql = "SELECT " + content
        # pattern = r'SELECT\s*```sql ([^`]*).*'
        # sql = re.sub(pattern, r'\1', sql)
        # return sql

    @staticmethod
    def __post_process(sqls: List[str]) -> List[str]:
        result = []
        for sql in sqls:
            sql = sql.replace("\n", " ")
            result.append(sql)
        return result
