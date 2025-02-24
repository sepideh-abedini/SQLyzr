"""
Generate questions for LLMs and save it as a task
"""
import json
from dataclasses import dataclass

import tqdm
from loguru import logger

from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.file_gen import FileGenerator
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.prompt.prompt_builder import prompt_factory
from src.third_party.dail.utils.data_builder import load_data
from src.third_party.dail.utils.enums import LLM
from src.third_party.dail.utils.utils import cost_estimate


class DailSecondQuestionGenerator(FileGenerator):
    __dail_conf: DailConfig
    __run_conf: SingleRunConfig

    def __init__(self, dail_conf: DailConfig, run_conf: SingleRunConfig, out_path: str):
        super().__init__(out_path)
        self.__dail_conf = dail_conf
        self.__run_conf = run_conf

    def _run_internal(self):
        dail_conf = self.__dail_conf
        run_conf = self.__run_conf

        # load test dataset here
        data = load_data(run_conf.dataset_config, dail_conf)

        databases = data.get_databases()

        # select the prompt
        params = self.__dail_conf.params
        prompt = prompt_factory(params.prompt_repr, params.k_shot, params.example_type, params.selector_type)(data=data,
                                                                                                              tokenizer=params.tokenizer)
        logger.info("Prompt done!")

        # format all questions
        questions = list()
        token_cnt = 0

        # choose split
        cross_domain = params.split == "train"

        for question_json in tqdm.tqdm(data.get_test_json()):
            question_format = prompt.format(target=question_json,
                                            max_seq_len=params.max_seq_len,
                                            max_ans_len=params.max_ans_len,
                                            scope_factor=params.scope_factor,
                                            cross_domain=cross_domain)

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
            # example_quality_each = prompt.get_example_quality_for_each()
            pattern_similarity = prompt.get_pattern_similarity()
            # print(f"Example quality: {example_quality}")
            # print(f"Estimated cost for {LLM.GPT_4}: {cost_gpt_35_turbo * 20}")
            # print(f"Estimated cost for {LLM.GPT_35_TURBO}: {cost_gpt_35_turbo}")
            # print(f"Estimated cost for {LLM.TEXT_DAVINCI_003}: {cost_text_davinci_003}")

            # save questions
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

            # path_generate = f"dataset/process/{args.data_type.upper()}-{args.split.upper()}_{prompt.name}_CTX-{args.max_ans_len}_ANS-{args.max_seq_len}"
            json.dump(task, open(dail_conf.second_questions_path(), "w"), indent=4)

            # os.makedirs(path_generate, exist_ok=True)
            # json.dump(task, open(os.path.join(path_generate, "questions.json"), "w"), indent=4)
