import os
import time

import backoff
from openai import AsyncClient
from openai.types.chat import ChatCompletion

from src.gpt.gateway.gateway_exceptions import GptRateLimitException
from src.gpt.models import BatchInputRequest, SqlyzrChatCompletion
from src.gpt.tracker.gpt_tracker import GptUsageTracker
from src.util.logger import debug_log


class GptGateway:
    __client: AsyncClient
    __tracker: GptUsageTracker

    def __init__(self):
        self.__client = AsyncClient(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=60
        )
        self.__tracker = GptUsageTracker.get_instance()

    @backoff.on_exception(backoff.constant, interval=30, max_tries=100, exception=GptRateLimitException)
    async def track_and_send(self, request: BatchInputRequest) -> SqlyzrChatCompletion:
        debug_log(f"Sending [{request.custom_id}]")
        tokens = request.get_token_usage()
        can_send = await self.__tracker.check_limit(tokens)
        if can_send:
            usage = await self.__tracker.add_usage(tokens)
            result = await self._send_without_tracking(request)
            completion_seconds = int(time.time()) - int(result.created)
            result_extended = SqlyzrChatCompletion(**result.dict(), completion_seconds=completion_seconds)
            usage.expire()
            return result_extended
        else:
            raise GptRateLimitException()

    async def _send_without_tracking(self, request: BatchInputRequest) -> ChatCompletion:
        debug_log("Sending GPT Request")
        result = await self.__client.chat.completions.create(
            **request.body.dict()
        )
        debug_log("Received GPT Response")
        return result
