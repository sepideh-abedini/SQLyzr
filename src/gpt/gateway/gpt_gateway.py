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
    client: AsyncClient
    tracker: GptUsageTracker

    def __init__(self):
        self.client = AsyncClient(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=20
        )
        self.tracker = GptUsageTracker.get_instance()

    async def send_without_tracking(self, request: BatchInputRequest) -> ChatCompletion:
        debug_log("Sending GPT Request")
        result = await self.client.chat.completions.create(
            **request.body.dict()
        )
        debug_log("Received GPT Response")
        return result

    @backoff.on_exception(backoff.constant, interval=30, max_tries=100, exception=GptRateLimitException)
    async def track_and_send(self, request: BatchInputRequest) -> SqlyzrChatCompletion:
        debug_log(f"Sending [{request.custom_id}]")
        tokens = request.get_token_usage()
        can_send = await self.tracker.check_limit(tokens)
        if can_send:
            usage = await self.tracker.add_usage(tokens)
            result = await self.send_without_tracking(request)
            result_extended = SqlyzrChatCompletion(**result.dict(), completed_at=int(time.time()))
            usage.expire()
            return result_extended
        else:
            raise GptRateLimitException()




