"""
Generate questions for LLMs and save it as a task
"""
import argparse
import os
import sys
import json

from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.file_gen import FileGenerator
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.prompt.prompt_builder import prompt_factory
from src.third_party.dail.utils.data_builder import load_data
from src.third_party.dail.utils.enums import LLM
from src.third_party.dail.utils.utils import cost_estimate

from tqdm import tqdm

DATASET_TYPE = "spider"
TOKENIZER = 'gpt-3.5-turbo'
MAX_SEQ_LEN = 4096
MAX_ANS_LEN = 200
PROMPT_REPR = "SQL"
K_SHOT = 9
EXAMPLE_TYPE = "QA"
SELECTOR_TYPE = "EUCDISQUESTIONMASK"
SCOPE_FACTOR = 100
SPLIT = "test"


class DailQuestionGenerator(FileGenerator):
    __dail_conf: DailConfig
    __run_conf: SingleRunConfig

    def __init__(self, dail_conf: DailConfig, run_conf: SingleRunConfig):
        super().__init__(dail_conf.questions_path())
        self.__dail_conf = dail_conf
        self.__run_conf = run_conf

    def _run_internal(self):
        dail_conf = self.__dail_conf
        run_conf = self.__run_conf

        # load test dataset here
        data = load_data(DATASET_TYPE, tables_path=run_conf.dataset_config.get_tables_path(),
                         input_path=run_conf.dataset_config.get_test_path(),
                         db_dir=run_conf.dataset_config.get_db_path(),
                         schema_links_path=dail_conf.schema_path())

        # Read all tables into a dict
        databases = data.get_databases()

        # select the prompt
        prompt = prompt_factory(PROMPT_REPR, K_SHOT, EXAMPLE_TYPE, SELECTOR_TYPE)(data=data, tokenizer=TOKENIZER)

        # format all questions
        questions = list()
        token_cnt = 0

        # choose split
        cross_domain = SPLIT == "train"

        for question_json in data.get_train_json():
            question_format = prompt.format(target=question_json,
                                            max_seq_len=MAX_SEQ_LEN,
                                            max_ans_len=MAX_SEQ_LEN,
                                            scope_factor=SCOPE_FACTOR,
                                            cross_domain=cross_domain)

            questions.append(question_format)

            token_cnt += question_format["prompt_tokens"]

        # cost estimated
        token_cnt = float(token_cnt) / len(questions)
        # print(f"Total {len(questions)} questions, {token_cnt} tokens per prompt, {token_cnt / len(questions)} tokens per question")

        n_total_tokens = len(questions) * MAX_ANS_LEN + token_cnt
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
        json.dump(task, open(dail_conf.questions_path(), "w"), indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables", type=str)
    parser.add_argument("--db_dir", type=str)
    parser.add_argument("--schema_links", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--input", type=str)
    args = parser.parse_args()

    generate_questions(tables_path=args.tables, db_dir=args.db_dir, schema_links_path=args.schema_links,
                       output_path=args.output, input_path=args.input)
