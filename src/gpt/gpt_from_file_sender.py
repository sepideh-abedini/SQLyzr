import asyncio
from abc import ABC, abstractmethod
from typing import List, Type, TypeVar

from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from src.eval.lib import Timer
from src.gpt.gpt_batch_gateway import GptBatchGateway
from src.gpt.gpt_gateway import GptGateway, FormattedGptGateway
from src.gpt.models import BatchInputRequest


class GptFromFileSender(ABC):
    async def send_and_save(self, in_path: str, out_path: str):
        responses = await self.send_from_file(in_path)
        self.save_to_file(responses, out_path)

    @abstractmethod
    async def send_from_file(self, in_path: str) -> list[ChatCompletion]:
        pass

    def save_to_file(self, responses: list[ChatCompletion], out_path: str):
        out_file = open(out_path, "w")
        for response in responses:
            out_file.write(f"{response.json()}\n")
        out_file.close()


class GptBatchSender(GptFromFileSender):
    gateway: GptBatchGateway

    def __init__(self):
        self.gateway = GptBatchGateway()

    async def send_from_file(self, in_path: str) -> list[ChatCompletion]:
        output = await self.gateway.send_batch(in_path)
        result = list(map(lambda o: o.response.body, output))
        return result


class GptSingleSender(GptFromFileSender):
    gateway: GptGateway

    def __init__(self):
        self.gateway = GptGateway()

    async def send_from_file(self, in_path: str):
        reqs = self.load_reqs_from_file(in_path)
        timer = Timer()
        timer.start()
        responses = await self.send_reqs(reqs)
        with open(f"{in_path}.time", "w") as file:
            file.write(f"{timer.stop().total_seconds()}\n")
        return responses

    async def send_reqs(self, reqs: List[BatchInputRequest]) -> List[ChatCompletion]:
        futures = []
        for req in reqs:
            future = self.send_single_req(req)
            futures.append(future)
            print(f"{req.custom_id} sent")
        resps = await asyncio.gather(*futures)
        return resps

    async def send_single_req(self, req: BatchInputRequest):
        return await self.gateway.track_and_send(req)

    def load_reqs_from_file(self, in_path) -> List[BatchInputRequest]:
        in_file = open(in_path)
        reqs = []
        for line in in_file.readlines():
            req = BatchInputRequest.model_validate_json(line)
            reqs.append(req)
        return reqs


T = TypeVar('T', bound=BaseModel)


class GptFormattedSingleSender(GptSingleSender):
    response_format: Type[T]

    def __init__(self, response_format: Type[T]):
        super().__init__()
        self.response_format = response_format
        self.gateway = FormattedGptGateway(response_format)
