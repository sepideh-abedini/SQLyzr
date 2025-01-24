from abc import ABC
from typing import Callable, List

import pandas as pd

from src.eval.single_run_config import SingleRunConfig
from src.gpt.gpt_from_file_sender import GptBatchSender, GptSingleSender
from src.gpt.models import BatchInputRequest
from src.parse.parser import SqlParser

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
