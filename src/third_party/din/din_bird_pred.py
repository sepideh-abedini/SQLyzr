import re
from typing import List

from src.eval.single_run_config import SingleRunConfig
from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.models import BatchInputRequest
from src.parse.parser import SqlParser
from src.pred.predictor import Predictor, process_responses, load_data
from src.third_party.din.bird.bird_prompt_maker import schema_linking_prompt, classification_prompt, easy_prompt, \
    medium_prompt, hard_prompt, correction_prompt
from src.third_party.din.bird.utils import table_descriptions_parser, get_database_schema, extract_schema_links, \
    extract_label_and_sub_questions, extract_sql_query, extract_revised_sql_query
from src.third_party.din.config import DinConfig
from src.third_party.din.prompt_maker import PromptMaker


class DinBirdPredictor(Predictor):
    __conf: DinConfig
    __prompt_maker: PromptMaker
    __gpt_sender: GptFileSender
    __schema_links: List[str]
    __classifs: List[str]
    __pred_classes: List[str]
    __sqls: List[str]
    __parser: SqlParser
    __schemas: List[str]
    __column_descriptions: List[str]
    __hints: List[str]

    def __init__(self, run_conf: SingleRunConfig):
        super().__init__(run_conf)
        self.__conf = DinConfig(run_conf.get_pred_path())
        self.__prompt_maker = PromptMaker(self._run_conf.dataset_config.get_tables_path())

    def __preprocess(self):
        examples = load_data(self._run_conf.dataset_config.get_test_path()).to_dict("records")
        self.__hints = []
        self.__schemas = []
        self.__column_descriptions = []
        for i, example in enumerate(examples):
            db_id = example['db_id']
            question = example['question']
            columns_descriptions = table_descriptions_parser(
                self._run_conf.dataset_config.get_db_description_path(db_id))
            schema = get_database_schema(self._run_conf.dataset_config.get_db_file_path(db_id))
            self.__hints.append(example['evidence'])
            self.__column_descriptions.append(columns_descriptions)
            self.__schemas.append(schema)

    async def _run_internal(self):
        conf = self.__conf

        self.__preprocess()

        self._gen_batch_file(conf.get_path("schema", "in"), self.__generate_schema_req)

        await self._ask_file(conf.get_path("schema", "in"), conf.get_path("schema", "out"))

        self.__schema_links = process_responses(conf.get_path("schema", "out"), self.__process_schema_response)

        self._gen_batch_file(conf.get_path("classif", "in"), self.__generate_classif_req)

        await self._ask_file(conf.get_path("classif", "in"), conf.get_path("classif", "out"))

        self.__classifs = process_responses(conf.get_path("classif", "out"), lambda i, s: s)

        self._gen_batch_file(conf.get_path("sql", "in"), self.__create_sql_prompt)

        await self._ask_file(conf.get_path("sql", "in"), conf.get_path("sql", "out"))

        self.__sqls = process_responses(conf.get_path("sql", "out"), self.__process_sql_responses)

        self._gen_batch_file(conf.get_path("sql_debug", "in"), self.__create_debug_sql_prompt)

        await self._ask_file(conf.get_path("sql_debug", "in"), conf.get_path("sql_debug", "out"))

        self.__sqls = process_responses(conf.get_path("sql_debug", "out"), self.__process_sql_debug_response)

        sqls = self.__post_process(self.__sqls)

        self._save_sqls(sqls)

    def __generate_schema_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        columns_descriptions = self.__column_descriptions[i]
        schema = self.__schemas[i]
        hint = self.__hints[i]
        prompt = schema_linking_prompt.format(question=question, schema=schema, hint=hint,
                                              columns_descriptions=columns_descriptions)
        return self._create_batch_req(f"s{i}", prompt, self.__conf.default_params)

    def __generate_classif_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        schema_links = self.__schema_links[i]
        columns_descriptions = self.__column_descriptions[i]
        schema = self.__schemas[i]
        hint = self.__hints[i]
        prompt = classification_prompt.format(question=question,
                                              schema=schema,
                                              hint=hint,
                                              columns_descriptions=columns_descriptions,
                                              schema_links=schema_links)
        return self._create_batch_req(f"c{i}", prompt, self.__conf.default_params)

    def __create_sql_prompt(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        schema_links = self.__schema_links[i]
        classification = self.__classifs[i]
        columns_descriptions = self.__column_descriptions[i]
        schema = self.__schemas[i]
        hint = self.__hints[i]
        label, sub_questions = extract_label_and_sub_questions(classification)
        if "EASY" in label:
            prompt = easy_prompt.run(
                question=question,
                schema=schema,
                hint=hint,
                columns_descriptions=columns_descriptions,
                schema_links=schema_links)
        elif "NON-NESTED" in label:
            prompt = medium_prompt.format(question=question,
                                          schema=schema,
                                          hint=hint,
                                          columns_descriptions=columns_descriptions,
                                          schema_links=schema_links)
        else:
            prompt = hard_prompt.format(
                question=question,
                schema=schema,
                hint=hint,
                columns_descriptions=columns_descriptions,
                schema_links=schema_links,
                sub_questions=sub_questions)
        return self._create_batch_req(f"s{i}", prompt, self.__conf.default_params)

    def __create_debug_sql_prompt(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        sql_query = self.__sqls[i]
        columns_descriptions = self.__column_descriptions[i]
        schema = self.__schemas[i]
        hint = self.__hints[i]
        prompt = correction_prompt.format(question=question,
                                          schema=schema,
                                          columns_descriptions=columns_descriptions,
                                          hint=hint,
                                          sql_query=sql_query)
        return self._create_batch_req(f"sd{i}", prompt, self.__conf.debug_params)

    @staticmethod
    def __process_schema_response(i: int, content: str) -> str:
        schema_links = extract_schema_links(content)
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
        return extract_sql_query(content)

    def __process_sql_debug_response(self, i: int, content: str) -> str:
        return extract_revised_sql_query(content)

    @staticmethod
    def __post_process(sqls: List[str]) -> List[str]:
        result = []
        for sql in sqls:
            sql = sql.replace("\n", " ")
            result.append(sql)
        return result
