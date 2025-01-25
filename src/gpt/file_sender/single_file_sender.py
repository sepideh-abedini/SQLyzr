import asyncio
from typing import List

from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.gateway.gpt_gateway import GptGateway
from src.gpt.models import SqlyzrChatCompletion, BatchInputRequest
from src.util.logger import debug_log
from src.util.model_utils import read_jsonl


class GptSingleSender(GptFileSender):
    __gateway: GptGateway

    def __init__(self):
        self.__gateway = GptGateway()

    async def __send_reqs(self, reqs: List[BatchInputRequest]) -> List[SqlyzrChatCompletion]:
        futures = []
        for req in reqs:
            future = self.__send_single_req(req)
            futures.append(future)
            debug_log(f"Request {req.custom_id} initiated")
        resps = list(await asyncio.gather(*futures))
        return resps

    async def __send_single_req(self, req: BatchInputRequest) -> SqlyzrChatCompletion:
        return await self.__gateway.track_and_send(req)

    async def _send_file(self, in_path: str) -> list[SqlyzrChatCompletion]:
        reqs = read_jsonl(in_path, BatchInputRequest)
        responses = await self.__send_reqs(reqs)
        return responses
