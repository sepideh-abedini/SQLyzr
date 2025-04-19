import os

import backoff
from diskcache import Cache
from openai import AsyncClient, RateLimitError
from openai.types.chat import ChatCompletion

from src.gpt.gateway.gateway_exceptions import GptRateLimitException
from src.gpt.gateway.single.token_tracker import GptTokenTracker
from src.gpt.models import BatchInputRequest
from loguru import logger

cache = Cache("/tmp/gpt_cache")

GPT_CACHE = bool(int(os.environ.get("GPT_CACHE", 0)))


class GptGateway:
    _client: AsyncClient
    __tracker: GptTokenTracker

    def __init__(self):
        self._client = AsyncClient(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=int(os.getenv("OPENAI_TIMEOUT", 60))
        )
        self.__tracker = GptTokenTracker.get_instance()

    @backoff.on_exception(backoff.constant, interval=10, max_tries=100, exception=GptRateLimitException)
    async def track_and_send(self, request: BatchInputRequest) -> ChatCompletion:
        s = str(request)
        if GPT_CACHE:
            if s in cache:
                return cache[s]
        logger.debug(f"Sending [{request.custom_id}]")
        tokens = request.get_token_usage()
        can_send = await self.__tracker.check_limit(tokens)
        if can_send:
            usage = await self.__tracker.add_usage(tokens)
            result = await self.send_without_tracking(request)
            logger.debug(f"TOKENS DIFF: {tokens}@{result.usage.total_tokens}")
            usage.expire()
            if GPT_CACHE:
                cache[s] = result
            return result
        else:
            raise GptRateLimitException()

    async def send_without_tracking(self, request: BatchInputRequest) -> ChatCompletion:
        logger.debug("Sending GPT Request")
        try:
            result = await self._client.chat.completions.create(
                **request.body.dict(), extra_headers={'custom_id': request.custom_id},
            )
            logger.debug("Received GPT Response")
        except RateLimitError as e:
            logger.warning(f"Rate Limit error: {e}")
            raise GptRateLimitException()
        return result
