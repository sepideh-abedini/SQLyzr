import numpy as np
import tqdm

from src.third_party.dail.prompt.ExampleFormatTemplate import ExampleFormatTemplate
from src.third_party.dail.prompt.ExampleSelectorTemplate import BasicExampleSelector
from src.third_party.dail.prompt.PromptReprTemplate import BasicPrompt
from src.third_party.dail.utils.utils import get_tokenizer, count_tokens, jaccard_similarity


class BasicICLPrompt(object):
    SEP_EXAMPLE = "\n\n"

    name: str
    NUM_EXAMPLE: int
    target_formatter: BasicPrompt
    example_selector: BasicExampleSelector
    example_format_template: ExampleFormatTemplate

    def __init__(self,name: str, tokenizer: str, num_examples: int, target_formatter: BasicPrompt = None,
                 example_selector: BasicExampleSelector = None, example_format_template: ExampleFormatTemplate = None,
                 *args, **kwargs):
        self.name = name
        self.NUM_EXAMPLE = num_examples
        self.tokenizer = get_tokenizer(tokenizer)
        self.example_qualities = []
        self.pattern_similarities = []
        self.target_formatter = target_formatter
        self.example_selector = example_selector
        self.example_format_template = example_format_template

    def record_example_quality(self, examples, target):
        quality_list = []
        for example in examples:
            quality_list.append(jaccard_similarity(example["query_skeleton"], target["query_skeleton"]))
        self.example_qualities.append(quality_list)

    def get_example_quality(self):
        if self.example_qualities:
            return np.mean([num for row in self.example_qualities for num in row])
        else:
            return 1

    def get_example_quality_for_each(self):
        if self.example_qualities:
            return [np.mean(row) for row in self.example_qualities]
        else:
            return []

    def record_pattern_similarity(self, examples, target):
        similarity_list = []
        for example in examples:
            similarity_list.append(jaccard_similarity(example["question_pattern"], target["question_pattern"]))
        self.pattern_similarities.append(similarity_list)

    def get_pattern_similarity(self):
        if self.pattern_similarities:
            return np.mean([num for row in self.pattern_similarities for num in row])
        else:
            return 1

    def format(self, target: dict, max_seq_len: int, max_ans_len: int, scope_factor: int, cross_domain=False, *args,
               **kwargs):
        # target question
        prompt_target = self.target_formatter.format_target(target)
        sum_tokens = count_tokens(prompt_target, tokenizer=self.tokenizer)

        if self.NUM_EXAMPLE != 0:
            # example questions
            examples = self.example_selector.get_examples(target, self.NUM_EXAMPLE * scope_factor, cross_domain=cross_domain)
            prompt_example = list()
            example_prefix = self.example_format_template.get_example_prefix()
            selected_examples = []
            # TODO:TQDM
            # for example in tqdm.tqdm(examples, total=len(examples), desc="Adding examples"):
            for example in examples:
                if cross_domain:
                    assert target["db_id"] != example["db_id"]

                example_format = self.example_format_template.format_example(example)

                forward_tokens = count_tokens(
                    example_prefix + self.SEP_EXAMPLE.join(prompt_example + [example_format, prompt_target]),
                    tokenizer=self.tokenizer)

                if forward_tokens + max_ans_len <= max_seq_len:
                    prompt_example.append(example_format)
                    sum_tokens = forward_tokens
                    selected_examples.append(example)

                    if len(prompt_example) >= self.NUM_EXAMPLE:
                        break

            self.record_example_quality(selected_examples, target)
            self.record_pattern_similarity(selected_examples, target)

            n_valid_example = len(prompt_example)
            if len(prompt_example) > 0:
                prompt = example_prefix + self.SEP_EXAMPLE.join(prompt_example + [prompt_target])
            else:
                prompt = self.SEP_EXAMPLE.join(prompt_example + [prompt_target])
        else:
            n_valid_example = 0
            prompt = prompt_target

        response_clean = " ".join(target["query"].split())[len("SELECT "):]
        return {
            "prompt_tokens": sum_tokens,
            "prompt": prompt,
            "response": response_clean,
            "n_examples": n_valid_example,
            "db_id": target["db_id"]
        }
