"""
Generate questions for LLMs and save it as a task
"""
import json
import os
from dataclasses import dataclass
from functools import partial

import tqdm
from loguru import logger

from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.file_gen import FileGenerator
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.prompt.prompt_builder import prompt_factory
from src.third_party.dail.utils.data_builder import load_data
from src.third_party.dail.utils.enums import LLM
from src.third_party.dail.utils.utils import cost_estimate
from src.util.multi_thread_utils import exec_multi_process_chunked, exec_multi_process

SQLYZR_DEVICE = os.environ.get("SQLYZR_DEVICE", "cpu")


class PromptWorker:
    def __init__(self, prompt, params, cross_doamin):
        self.prompt = prompt
        self.params = params
        self.cross_domain = cross_doamin

    def format(self, question_json):
        question_format = self.prompt.format(target=question_json,
                                             max_seq_len=self.params.max_seq_len,
                                             max_ans_len=self.params.max_ans_len,
                                             scope_factor=self.params.scope_factor,
                                             cross_domain=self.cross_domain)
        return question_format

    def format_list(self, data):
        return list(tqdm.tqdm(map(self.format, data), total=len(data)))


class DailQuestionGenerator(FileGenerator):
    __dail_conf: DailConfig
    __run_conf: SingleRunConfig
    second_stage: bool

    def __init__(self, dail_conf: DailConfig, run_conf: SingleRunConfig, out_path: str, second_stage: bool = False):
        super().__init__(out_path)
        self.__dail_conf = dail_conf
        self.__run_conf = run_conf
        self.second_stage = second_stage

    def _run_internal(self):
        dail_conf = self.__dail_conf
        run_conf = self.__run_conf

        # load test dataset here
        data = load_data(run_conf.dataset_config, dail_conf)
        logger.info("Loading data done!")

        databases = data.get_databases()

        params = self.__dail_conf.params
        prompt = prompt_factory(params, data, self.second_stage)

        logger.info("Prompt done!")

        # format all questions
        questions = list()
        token_cnt = 0

        # choose split
        cross_domain = params.split == "train"

        worker = PromptWorker(prompt, params, cross_domain)

        test_data = data.get_test_json()
        # formats = exec_multi_process(worker.format_list, test_data, 8)
        if SQLYZR_DEVICE == "mps":
            formats = list(tqdm.tqdm(map(worker.format, test_data), total=len(test_data)))
        else:
            formats = exec_multi_process(worker.format, test_data)

        # for question_json in tqdm.tqdm(test_data):
        for question_format in formats:
            # question_format = prompt.format(target=question_json,
            #                                 max_seq_len=params.max_seq_len,
            #                                 max_ans_len=params.max_ans_len,
            #                                 scope_factor=params.scope_factor,
            #                                 cross_domain=cross_domain)
            # question_format = worker.format(question_json)
            questions.append(question_format)

            token_cnt += question_format["prompt_tokens"]

            # cost estimated
            token_cnt = float(token_cnt) / len(questions)
            logger.debug(
                f"Total {len(questions)} questions, {token_cnt} tokens per prompt, {token_cnt / len(questions)} tokens per question")

            n_total_tokens = int(len(questions) * params.max_ans_len + token_cnt)
            cost_gpt_35_turbo = cost_estimate(n_total_tokens, LLM.GPT_35_TURBO)
            cost_text_davinci_003 = cost_estimate(n_total_tokens, LLM.TEXT_DAVINCI_003)
            example_quality = prompt.get_example_quality()
            pattern_similarity = prompt.get_pattern_similarity()

            task = {
                "args": "",
                "costs": {
                    "prompt_tokens_per_prompt": token_cnt,
                    "gpt-4": cost_gpt_35_turbo * 20,
                    "gpt-3.5-turbo": cost_gpt_35_turbo,
                    "text-davinci-003": cost_text_davinci_003,
                    "example_quality": example_quality,
                    "pattern_similarity": pattern_similarity,
                    # "example_quality_for_each": example_quality_each
                },
                "questions": questions
            }

        if not self.second_stage:
            save_path = dail_conf.questions_path()
        else:
            save_path = dail_conf.second_questions_path()

        with open(save_path, "w") as out_file:
            json.dump(task, out_file, indent=4)
