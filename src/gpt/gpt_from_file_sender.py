import asyncio
import os
from abc import ABC, abstractmethod
from typing import List, Type, TypeVar

from openai.types import Batch
from pydantic import BaseModel

from src.gpt.gpt_batch_gateway import GptBatchGateway
from src.gpt.gpt_gateway import GptGateway, FormattedGptGateway
from src.gpt.gpt_usage_stats import GptUsageStats
from src.gpt.models import BatchInputRequest
from src.gpt.sqlyzr_chat_completion import SqlyzrChatCompletion
from src.util.logger import log, debug_log


class GptFromFileSender(ABC):
    async def send_and_save(self, in_path: str, out_path: str) -> GptUsageStats:
        debug_log(f"Asking GPT {in_path} ==> {out_path}")
        if os.path.exists(out_path):
            debug_log(f"Output path exists: {out_path}, skip asking gpt.")
        else:
            responses = await self.send_from_file(in_path)
            self.save_to_file(responses, out_path)
        usage = self.get_usage(in_path, out_path)
        return usage

    @abstractmethod
    async def send_from_file(self, in_path: str) -> list[SqlyzrChatCompletion]:
        pass

    @abstractmethod
    def get_usage(self, in_path: str, out_path: str) -> GptUsageStats:
        pass

    def save_to_file(self, responses: list[SqlyzrChatCompletion], out_path: str):
        out_file = open(out_path, "w")
        for response in responses:
            out_file.write(f"{response.json()}\n")
        out_file.close()

    def load_resps_from_file(self, out_path) -> List[SqlyzrChatCompletion]:
        out_file = open(out_path)
        resps = []
        for line in out_file.readlines():
            res = SqlyzrChatCompletion.model_validate_json(line)
            resps.append(res)
        return resps


class GptBatchSender(GptFromFileSender):
    gateway: GptBatchGateway

    def __init__(self):
        self.gateway = GptBatchGateway()

    async def send_from_file(self, in_path: str) -> list[SqlyzrChatCompletion]:
        output, usage = await self.gateway.send_batch(in_path)
        result = list(map(lambda o: o.response.body, output))
        return result, usage

    def get_usage(self, in_path: str, out_path: str) -> GptUsageStats:
        with open(f"{in_path}.batch.stats.json") as file:
            batch = Batch.model_validate_json(file.read())
        completion_time = batch.completed_at - batch.created_at
        resps = self.load_resps_from_file(out_path)
        total_tokens = 0
        for res in resps:
            total_tokens += res.response.body.usage.total_tokens
        usage = GptUsageStats(total_time=completion_time, total_tokens=total_tokens)
        return usage


class GptSingleSender(GptFromFileSender):
    gateway: GptGateway

    def __init__(self):
        self.gateway = GptGateway()

    async def send_from_file(self, in_path: str) -> list[SqlyzrChatCompletion]:
        reqs = self.load_reqs_from_file(in_path)
        responses = await self.send_reqs(reqs)
        return responses

    async def send_reqs(self, reqs: List[BatchInputRequest]) -> List[SqlyzrChatCompletion]:
        futures = []
        for req in reqs:
            future = self.send_single_req(req)
            futures.append(future)
            print(f"{req.custom_id} sent")
        resps = await asyncio.gather(*futures)
        return resps

    async def send_single_req(self, req: BatchInputRequest) -> SqlyzrChatCompletion:
        return await self.gateway.track_and_send(req)

    def load_reqs_from_file(self, in_path) -> List[BatchInputRequest]:
        in_file = open(in_path)
        reqs = []
        for line in in_file.readlines():
            req = BatchInputRequest.model_validate_json(line)
            reqs.append(req)
        return reqs

    def get_usage(self, in_path: str, out_path: str) -> GptUsageStats:
        resps = self.load_resps_from_file(out_path)
        total_time = 0
        total_tokens = 0
        for res in resps:
            total_time += res.completed_at - res.created
            total_tokens += res.usage.total_tokens
        return GptUsageStats(total_time=total_time, total_tokens=total_tokens)


T = TypeVar('T', bound=BaseModel)


class GptFormattedSingleSender(GptSingleSender):
    response_format: Type[T]

    def __init__(self, response_format: Type[T]):
        super().__init__()
        self.response_format = response_format
        self.gateway = FormattedGptGateway(response_format)
