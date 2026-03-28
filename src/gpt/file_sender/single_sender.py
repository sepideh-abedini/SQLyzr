import os
from typing import List

from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.gateway.gateway import GptGateway
from src.gpt.models import BatchInputRequest, BatchInputResponse
from src.util.async_utils import apply_async
from src.util.model_utils import read_jsonl


class GptSingleSender(GptFileSender):
    _gateway: GptGateway

    def __init__(self):
        super().__init__()
        self._gateway = GptGateway()

    async def __send_reqs(self, reqs: List[BatchInputRequest]) -> List[BatchInputResponse]:
        # semaphore = asyncio.Semaphore(self.ASYNC_BATCH)
        # results = []

        # async def sem_task(req: BatchInputRequest):
        #     async with semaphore:
        #         logger.debug(f"Request {req.custom_id} initiated")
        #         return await self.__send_single_req(req)

        # tasks = [asyncio.create_task(sem_task(req)) for req in reqs]
        # results = await tqdm.gather(*tasks, desc="Waiting for GPT response")
        results = await apply_async(self.__send_single_req, reqs, "Waiting for GPT response")
        return results

    async def __send_single_req(self, req: BatchInputRequest) -> BatchInputResponse:
        return await self._gateway.track_and_send(req)

    async def _send_file(self, in_path: str) -> list[BatchInputResponse]:
        reqs = read_jsonl(in_path, BatchInputRequest)
        responses = await self.__send_reqs(reqs)
        return responses
