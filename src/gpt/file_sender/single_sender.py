from typing import List

from openai.types.chat import ChatCompletion
from tqdm.asyncio import tqdm

from src.eval.lib import Timer
from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.gateway.gateway import GptGateway
from src.gpt.models import BatchInputRequest
from src.util.logger import debug_log
from src.util.model_utils import read_jsonl


class GptSingleSender(GptFileSender):
    _gateway: GptGateway

    def __init__(self):
        super().__init__()
        self._gateway = GptGateway()

    async def __send_reqs(self, reqs: List[BatchInputRequest]) -> List[ChatCompletion]:
        futures = []
        for req in reqs:
            future = self.__send_single_req(req)
            futures.append(future)
            debug_log(f"Request {req.custom_id} initiated")
        resps = list(await tqdm.gather(desc="Waiting for responses", *futures))
        self._total_tokens = sum(map(lambda res: res.usage.total_tokens if res.usage else 0, resps))
        return resps

    async def __send_single_req(self, req: BatchInputRequest) -> ChatCompletion:
        return await self._gateway.track_and_send(req)

    async def _send_file(self, in_path: str) -> list[ChatCompletion]:
        reqs = read_jsonl(in_path, BatchInputRequest)
        timer = Timer.start()
        responses = await self.__send_reqs(reqs)
        self._total_time = timer.lap()
        return responses
