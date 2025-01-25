from abc import ABC, abstractmethod
from typing import Callable, List, TypeVar, Type

import pandas as pd
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from src.eval.single_run_config import SingleRunConfig
from src.gpt.file_sender.batch_sender import GptBatchFileSender
from src.gpt.file_sender.single_sender import GptSingleSender
from src.gpt.models import BatchInputRequest
from src.parse.parser import SqlParser
from src.util.model_utils import read_jsonl

ResponseProcessor = Callable[[int, str], str]

BatchRequestGenerator = Callable[[int, str, str], BatchInputRequest]


def load_data(input_path: str):
    return pd.read_json(input_path)


class Predictor(ABC):
    _run_conf: SingleRunConfig

    def __init__(self, run_conf: SingleRunConfig):
        self._run_conf = run_conf
        self.__parser = SqlParser()
        if self._run_conf.batch:
            self.__gpt_sender = GptBatchFileSender()
        else:
            self.__gpt_sender = GptSingleSender()

    @abstractmethod
    async def run(self):
        pass

    async def _ask_file(self, in_path: str, out_path: str):
        return await self.__gpt_sender.send_and_save(in_path, out_path)

    def _gen_batch_file(self, file_path: str, gen_req: BatchRequestGenerator):
        examples = load_data(self._run_conf.dataset_config.get_data_path()).to_dict("records")
        file = open(file_path, "w")
        for i, example in enumerate(examples):
            db_id = example['db_id']
            question = example['question']
            request = gen_req(i, db_id, question)
            file.write(f"{request.json()}\n")
        file.close()

    def _create_batch_req(self, idx: str, prompt: str, extra_params):
        extra_params['temperature'] = self._run_conf.temp
        return BatchInputRequest.create_prompt_req(idx, prompt, extra_params)

    def _save_sqls(self, sqls: List[str]):
        file = open(self._run_conf.get_pred_path(), 'w')
        for sql in sqls:
            file.write(f"{sql}\n")
        file.close()


T = TypeVar('T', bound=BaseModel)


def identity_processor(i: int, content: T) -> T:
    return content


def process_responses(file_path: str, response_processor: ResponseProcessor = identity_processor) -> List[str]:
    responses = read_jsonl(file_path, ChatCompletion)
    results = []
    for i, response in enumerate(responses):
        content = response.choices[0].message.content
        processed = response_processor(i, content)
        results.append(processed)
    return results


U = TypeVar('U')


def process_formatted_responses(file_path: str, response_format: Type[T],
                                response_processor: Callable[[int, T], U] = identity_processor) -> List[U]:
    responses = read_jsonl(file_path, ChatCompletion)
    results = []
    for i, response in enumerate(responses):
        content = response_format.model_validate(response.choices[0].message.parsed)
        processed = response_processor(i, content)
        results.append(processed)
    return results
