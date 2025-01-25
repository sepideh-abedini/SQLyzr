import json
from abc import ABC
from typing import Callable, List, TypeVar, Type

import pandas as pd
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from src.eval.single_run_config import SingleRunConfig
from src.gpt.gpt_from_file_sender import GptBatchSender, GptSingleSender
from src.gpt.models import BatchInputRequest
from src.parse.parser import SqlParser

ResponseProcessor = Callable[[int, str], str]

BatchRequestGenerator = Callable[[int, str, str], BatchInputRequest]


def load_data(input_path: str):
    return pd.read_json(input_path)


class Predictor(ABC):
    run_conf: SingleRunConfig

    def __init__(self, run_conf: SingleRunConfig):
        self.run_conf = run_conf
        self.parser = SqlParser()
        if self.run_conf.batch:
            self.gpt_sender = GptBatchSender()
        else:
            self.gpt_sender = GptSingleSender()

    async def ask_file(self, in_path: str, out_path: str):
        return await self.gpt_sender.send_and_save(in_path, out_path)

    def gen_batch_file(self, file_path: str, gen_req: BatchRequestGenerator):
        examples = load_data(self.run_conf.dataset_config.get_data_path()).to_dict("records")
        file = open(file_path, "w")
        for i, example in enumerate(examples):
            db_id = example['db_id']
            question = example['question']
            request = gen_req(i, db_id, question)
            file.write(f"{request.json()}\n")
        file.close()

    def create_batch_req(self, idx: str, prompt: str, extra_params):
        extra_params['temperature'] = self.run_conf.temp
        return BatchInputRequest.create_prompt_req(idx, prompt, extra_params)

    def save_sqls(self, sqls: List[str]):
        file = open(self.run_conf.get_pred_path(), 'w')
        for sql in sqls:
            file.write(f"{sql}\n")
        file.close()


def load_responses(in_path: str) -> List[ChatCompletion]:
    file = open(in_path)
    data = []
    for line in file.readlines():
        response = json.loads(line)
        response = ChatCompletion.model_validate(response)
        data.append(response)
    return data


T = TypeVar('T', bound=BaseModel)


def identity_processor(i: int, content: T) -> T:
    return content


def process_responses(file_path: str, response_processor: ResponseProcessor = identity_processor) -> List[str]:
    responses = load_responses(file_path)
    results = []
    for i, response in enumerate(responses):
        content = response.choices[0].message.content
        processed = response_processor(i, content)
        results.append(processed)
    return results


U = TypeVar('U')


def process_formatted_responses(file_path: str, response_format: Type[T],
                                response_processor: Callable[[int, T], U] = identity_processor) -> List[U]:
    responses = load_responses(file_path)
    results = []
    for i, response in enumerate(responses):
        content = response_format.model_validate(response.choices[0].message.parsed)
        processed = response_processor(i, content)
        results.append(processed)
    return results
