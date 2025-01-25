import os

import backoff
from openai import AsyncClient
from openai.types.chat import ChatCompletion

from src.gpt.gateway.gateway_exceptions import GptRateLimitException
from src.gpt.gateway.single.token_tracker import GptTokenTracker
from src.gpt.models import BatchInputRequest
from src.util.logger import debug_log


class GptGateway:
    _client: AsyncClient
    __tracker: GptTokenTracker

    def __init__(self):
        self._client = AsyncClient(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=60
        )
        self.__tracker = GptTokenTracker.get_instance()

    @backoff.on_exception(backoff.constant, interval=30, max_tries=100, exception=GptRateLimitException)
    async def track_and_send(self, request: BatchInputRequest) -> ChatCompletion:
        debug_log(f"Sending [{request.custom_id}]")
        tokens = request.get_token_usage()
        can_send = await self.__tracker.check_limit(tokens)
        if can_send:
            usage = await self.__tracker.add_usage(tokens)
            result = await self.send_without_tracking(request)
            usage.expire()
            return result
        else:
            raise GptRateLimitException()

    async def send_without_tracking(self, request: BatchInputRequest) -> ChatCompletion:
        debug_log("Sending GPT Request")
        result = await self._client.chat.completions.create(
            **request.body.dict()
        )
        debug_log("Received GPT Response")
        return result
