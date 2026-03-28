import os.path
import time
from abc import ABC, abstractmethod
from typing import Callable, List, TypeVar, Type

import pandas as pd
from loguru import logger
from pydantic import BaseModel

from src.eval.lib import TimeLogger
from src.eval.single_run_config import SingleRunConfig
from src.gpt.file_sender.batch_sender import GptBatchFileSender
from src.gpt.file_sender.single_sender import GptSingleSender
from src.gpt.models import BatchInputRequest, BatchInputResponse, SqlyzrChatCompletion
from src.parse.parser import SqlParser
from src.util.file_utils import file_exists_not_forced
from src.util.log_util import alog
from src.util.model_utils import read_jsonl
from src.util.str_utils import shrink_whitespaces

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

    async def run(self):
        if file_exists_not_forced(self._run_conf.get_pred_path()):
            logger.info(f"Pred file exists: {self._run_conf.get_pred_path()}, skipping")
            self.save_tokens()
            return
        await self._run_internal()
        self.save_tokens()

    @abstractmethod
    async def _run_internal(self):
        pass

    @abstractmethod
    def get_out_batch_files(self) -> List[str]:
        pass

    def save_extra_numeric_metric(self, save_path, metric_extractor):
        all = []
        for file in self.get_out_batch_files():
            p = f"{self._run_conf.get_pred_path()}.{file}"
            data = read_jsonl(p)
            per_row_metrics = list(map(metric_extractor, data))
            all.append(per_row_metrics)
        sum_per_row = list(map(lambda s: sum(s), zip(*all)))
        with open(save_path, "w") as metric_file:
            metric_file.write("\n".join(map(str, sum_per_row)))

    def save_tokens(self):
        self.save_extra_numeric_metric(self._run_conf.get_tokens_path(),
                                       lambda r: r['usage']['total_tokens'] if 'usage' in r else 0)
        self.save_extra_numeric_metric(self._run_conf.get_time_path(),
                                       lambda r: r.get('finished', int(time.time()) - r['created']))

    @alog("Asking GPT")
    async def _ask_file(self, in_path: str, out_path: str):
        await self.__gpt_sender.send_and_save(in_path, out_path)

    def _gen_batch_file(self, file_path: str, gen_req: BatchRequestGenerator):
        examples = load_data(self._run_conf.dataset_config.get_test_path()).to_dict("records")
        with open(file_path, "w") as file:
            for i, example in enumerate(examples):
                db_id = example['db_id']
                question = example['question']
                request = gen_req(i, db_id, question)
                file.write(f"{request.json()}\n")

    def _create_batch_req(self, idx: str, prompt: str, extra_params):
        extra_params['temperature'] = self._run_conf.temp
        return BatchInputRequest.create_prompt_req(idx, prompt, extra_params)

    def _save_sqls(self, sqls: List[str]):
        with open(self._run_conf.get_pred_path(), 'w') as file:
            for sql in sqls:
                sql = shrink_whitespaces(sql)
                file.write(f"{sql}\n")


T = TypeVar('T', bound=BaseModel)


def identity_processor(i: int, content: T) -> T:
    return content


def process_responses(file_path: str, response_processor: ResponseProcessor = identity_processor) -> List[str]:
    time_logger = TimeLogger.start(f"ResponseProcessor:{file_path}")
    responses = read_jsonl(file_path, SqlyzrChatCompletion)
    results = []
    for i, response in enumerate(responses):
        content = response.choices[0].message.content
        processed = response_processor(i, content)
        results.append(processed)
    time_logger.lap()
    return results


U = TypeVar('U')


def process_formatted_responses(file_path: str, response_format: Type[T],
                                response_processor: Callable[[int, T], U] = identity_processor) -> List[U]:
    responses = read_jsonl(file_path, SqlyzrChatCompletion)
    results = []
    for i, response in enumerate(responses):
        content = response_format.model_validate(response.choices[0].message.parsed)
        processed = response_processor(i, content)
        results.append(processed)
    return results
