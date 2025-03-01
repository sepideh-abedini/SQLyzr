import json
import os
from typing import List

import tqdm
from loguru import logger
from openai.types.chat import ChatCompletion

from src.eval.lib import Timer
from src.eval.single_run_config import SingleRunConfig
from src.gpt.models import BatchInputRequest
from src.pred.predictor import Predictor
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.data_preprocess import DailSchemaLinksGenerator
from src.third_party.dail.generate_question import DailQuestionGenerator
from src.third_party.dail.sql_post_processor import DailSqlPostProcessorWorker
from src.util.model_utils import read_jsonl
from src.util.multi_thread_utils import exec_multi_process_flat, exec_multi_process


class DailPredictor(Predictor):
    __conf: DailConfig
    __questions: List[str]

    def __init__(self, run_conf: SingleRunConfig):
        super().__init__(run_conf)
        self.__conf = DailConfig(run_conf.get_pred_path())

    async def _run_internal(self):
        schema_links_gen = DailSchemaLinksGenerator(self.__conf, self._run_conf)
        usage = schema_links_gen.run()
        self._tracker.add_usage(usage)
        logger.info("Schema linking done!")

        question_gen = DailQuestionGenerator(self.__conf, self._run_conf, self.__conf.questions_path())
        usage = question_gen.run()
        self._tracker.add_usage(usage)
        logger.info("Question generation done!")

        self.__load_questions(self.__conf.questions_path())
        self._gen_batch_file(self.__conf.get_path("in"), self.__gen_sql_req)
        await self._ask_file(self.__conf.get_path("in"), self.__conf.get_path("out"))
        logger.info("SQL prediction done!")

        if os.path.exists(self.__conf.pre_test_result_path()):
            logger.info(f"Pre test result exists: {self.__conf.pre_test_result_path()}")
            with open(self.__conf.pre_test_result_path()) as file:
                sqls = file.readlines()
        else:
            timer = Timer.start()
            sqls = self.__process_responses(self.__conf.get_path("out"))
            with open(self.__conf.pre_test_result_path(), "w") as file:
                for sql in sqls:
                    file.write(f"{sql}\n")
            lap = timer.lap()
            with open(f"{self.__conf.pre_test_result_path()}.usage", "w") as usage_file:
                usage_file.write(f"{lap}")
        logger.info("SQL post porcessing done!")

        second_question_gen = DailQuestionGenerator(self.__conf, self._run_conf,
                                                    self.__conf.second_questions_path(), second_stage=True)
        usage = second_question_gen.run()
        self._tracker.add_usage(usage)
        logger.info("Second Question generation done!")

        self.__load_questions(self.__conf.second_questions_path())
        self._gen_batch_file(self.__conf.get_path("in.second"), self.__gen_sql_req)

        await self._ask_file(self.__conf.get_path("in.second"), self.__conf.get_path("out.second"))
        sqls = self.__process_responses(self.__conf.get_path("out.second"))
        logger.info("Second SQL generation done!")

        self._save_sqls(sqls)

    def __gen_sql_req(self, i: int, db_id: str, question: str) -> BatchInputRequest:
        dail_question = self.__questions[i]
        request = self._create_batch_req(f"i{i}", dail_question, self.__conf.gpt_params)
        return request

    def __load_questions(self, path: str):
        questions_json = json.load(open(path, "r"))
        self.__questions = [_["prompt"] for _ in questions_json["questions"]]

    def __process_responses(self, file_path) -> List[str]:
        with open(self._run_conf.dataset_config.get_test_path()) as data_file:
            data = json.load(data_file)
            db_ids = [example['db_id'] for example in data]
        responses = read_jsonl(file_path, ChatCompletion)
        pairs = list(zip(db_ids, responses))
        post_process_worker = DailSqlPostProcessorWorker(self.__conf, self._run_conf)
        results = exec_multi_process_flat(post_process_worker.post_proc_single, pairs, desc="Post processing SQLs")
        # results = exec_multi_process(post_process_worker.post_process_response, pairs)
        # results = list(tqdm.tqdm(map(post_process_worker.post_proc_single, pairs),total=len(pairs)))
        return results
