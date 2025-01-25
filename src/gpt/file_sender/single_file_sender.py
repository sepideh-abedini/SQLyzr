import asyncio
from typing import List

from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.gpt_gateway import GptGateway
from src.gpt.models import SqlyzrChatCompletion, BatchInputRequest
from src.util.logger import debug_log
from src.util.model_utils import read_jsonl


class GptSingleSender(GptFileSender):
    gateway: GptGateway

    def __init__(self):
        self.gateway = GptGateway()

    async def send_from_file(self, in_path: str) -> list[SqlyzrChatCompletion]:
        reqs = read_jsonl(in_path, BatchInputRequest)
        responses = await self.send_reqs(reqs)
        return responses

    async def send_reqs(self, reqs: List[BatchInputRequest]) -> List[SqlyzrChatCompletion]:
        futures = []
        for req in reqs:
            future = self.send_single_req(req)
            futures.append(future)
            debug_log(f"Request {req.custom_id} initiated")
        resps = await asyncio.gather(*futures)
        return resps

    async def send_single_req(self, req: BatchInputRequest) -> SqlyzrChatCompletion:
        return await self.gateway.track_and_send(req)
