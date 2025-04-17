from typing import List
import asyncio

from loguru import logger
from openai.types.chat import ChatCompletion
from tqdm.asyncio import tqdm

from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.gateway.gateway import GptGateway
from src.gpt.models import BatchInputRequest
from src.util.model_utils import read_jsonl


class GptSingleSender(GptFileSender):
    _gateway: GptGateway
    BATCH_COUNT = 10

    def __init__(self):
        super().__init__()
        self._gateway = GptGateway()

    async def __send_reqs(self, reqs: List[BatchInputRequest]) -> List[ChatCompletion]:
        semaphore = asyncio.Semaphore(self.BATCH_COUNT)
        results = []

        async def sem_task(req: BatchInputRequest):
            async with semaphore:
                logger.debug(f"Request {req.custom_id} initiated")
                return await self.__send_single_req(req)

        tasks = [asyncio.create_task(sem_task(req)) for req in reqs]
        for f in tqdm.as_completed(tasks, desc="Waiting for responses"):
            result = await f
            results.append(result)

        return results

    async def __send_single_req(self, req: BatchInputRequest) -> ChatCompletion:
        return await self._gateway.track_and_send(req)

    async def _send_file(self, in_path: str) -> list[ChatCompletion]:
        reqs = read_jsonl(in_path, BatchInputRequest)
        responses = await self.__send_reqs(reqs)
        return responses
