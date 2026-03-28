import json
import os
from typing import List

from loguru import logger

from src.eval.single_run_config import SingleRunConfig
from src.gpt.models import BatchInputRequest, SqlyzrChatCompletion
from src.model.predictor import Predictor
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.data_preprocess import DailSchemaLinksGenerator
from src.third_party.dail.generate_question import DailQuestionGenerator
from src.third_party.dail.sql_post_processor import DailSqlPostProcessorWorker
from src.util.log_util import log
from src.util.model_utils import read_jsonl
from src.util.multi_thread_utils import exec_multi_process


class DailPredictor(Predictor):
    __conf: DailConfig
    __questions: List[str]

    def __init__(self, run_conf: SingleRunConfig):
        super().__init__(run_conf)
        self.__conf = DailConfig(run_conf.get_pred_path())

    def get_out_batch_files(self) -> List[str]:
        return ["test.schema.jsonl",
                "questions.jsonl",
                "sql.out.jsonl",
                "second.questions.jsonl",
                "sql.out.second.jsonl"]

    async def _run_internal(self):
        logger.info("Starting DAIL Predictor")

        schema_links_gen = DailSchemaLinksGenerator(self.__conf, self._run_conf)
        schema_links_gen.run()

        question_gen = DailQuestionGenerator(self.__conf, self._run_conf, self.__conf.questions_path())
        question_gen.run()

        self.__load_questions(self.__conf.questions_path())
        self._gen_batch_file(self.__conf.get_path("in"), self.__gen_sql_req)
        await self._ask_file(self.__conf.get_path("in"), self.__conf.get_path("out"))

        sqls = self.__process_responses(self.__conf.get_path("out"), self.__conf.pre_test_result_path())

        second_question_gen = DailQuestionGenerator(self.__conf, self._run_conf,
                                                    self.__conf.second_questions_path(), second_stage=True)
        second_question_gen.run()

        self.__load_questions(self.__conf.second_questions_path())
        self._gen_batch_file(self.__conf.get_path("in.second"), self.__gen_second_sql_req)

        await self._ask_file(self.__conf.get_path("in.second"), self.__conf.get_path("out.second"))

        sqls = self.__process_responses(self.__conf.get_path("out.second"), self._run_conf.get_pred_path())
        self._save_sqls(sqls)

    def __gen_sql_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        dail_question = self.__questions[i]
        idx = f"dail_{self._run_conf.dataset_config.dataset_type}_sql_{i}"
        request = self._create_batch_req(idx, dail_question, self.__conf.gpt_params)
        return request

    def __gen_second_sql_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        dail_question = self.__questions[i]
        idx = f"dail_{self._run_conf.dataset_config.dataset_type}_second_sql_{i}"
        request = self._create_batch_req(idx, dail_question, self.__conf.gpt_params)
        return request

    def __load_questions(self, path: str):
        questions_json = read_jsonl(path)
        self.__questions = [_["prompt"] for _ in questions_json]

    @log("Dail response processing")
    def __process_responses(self, in_path, out_path) -> List[str]:
        if os.path.exists(out_path):
            logger.info(f"File exists, skipping preprocessing: {out_path}")
            with open(self.__conf.pre_test_result_path()) as file:
                sqls = file.readlines()
                return sqls
        with open(self._run_conf.dataset_config.get_test_path()) as data_file:
            data = json.load(data_file)
            db_ids = [example['db_id'] for example in data]
        responses = read_jsonl(in_path, SqlyzrChatCompletion)
        pairs = list(zip(db_ids, responses))
        post_process_worker = DailSqlPostProcessorWorker(self.__conf, self._run_conf)
        results = exec_multi_process(post_process_worker.post_proc_single, pairs, desc="Post processing SQLs")
        with open(out_path, "w") as file:
            for sql in results:
                file.write(f"{sql}\n")
        return results
