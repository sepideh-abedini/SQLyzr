import asyncio
from abc import ABC, abstractmethod
from typing import List

from openai.types.chat import ChatCompletion

from src.gpt.gpt_gateway import GptGateway
from src.gpt.models import BatchInputRequest


class GptFromFileSender(ABC):
    @abstractmethod
    async def send_from_file(self, in_path: str, out_path: str):
        pass


class GptSingleSender(GptFromFileSender):
    gateway: GptGateway

    def __init__(self):
        self.gateway = GptGateway()

    async def send_from_file(self, in_path: str, out_path: str):
        reqs = self.load_reqs_from_file(in_path)
        resps = await self.send_reqs(reqs)
        self.save_res_to_file(resps, out_path)

    async def send_reqs(self, reqs: List[BatchInputRequest]) -> List[ChatCompletion]:
        futures = []
        for req in reqs:
            future = self.gateway.track_and_send(req)
            futures.append(future)
            print(f"{req.custom_id} sent")
        resps = await asyncio.gather(*futures)
        return resps

    def load_reqs_from_file(self, in_path) -> List[BatchInputRequest]:
        in_file = open(in_path)
        reqs = []
        for line in in_file.readlines():
            req = BatchInputRequest.model_validate_json(line)
            reqs.append(req)
        return reqs

    def save_res_to_file(self, responses: list[ChatCompletion], out_path: str):
        out_file = open(out_path, "w")
        for response in responses:
            out_file.write(f"{response.json()}\n")
        out_file.close()
