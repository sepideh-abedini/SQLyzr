import os
import time

import backoff
from diskcache import Cache
from openai import AsyncClient, RateLimitError, api_key

from src.gpt.gateway.gateway_exceptions import GptRateLimitException, GptGatewayException
from src.gpt.gateway.single.token_tracker import GptTokenTracker
from src.gpt.models import BatchInputRequest, BatchInputResponse
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
    async def track_and_send(self, request: BatchInputRequest) -> BatchInputResponse:
        s = str(request)
        logger.debug(f"Sending [{request.custom_id}]")
        tokens = request.get_token_usage()
        can_send = await self.__tracker.check_limit(tokens)
        logger.debug(f"Checked tokens [{request.custom_id}]")
        if can_send:
            usage = await self.__tracker.add_usage(tokens)
            logger.debug(f"Usage added [{request.custom_id}]")
            result = await self.send_without_tracking(request)
            logger.debug(f"Request sent [{request.custom_id}]")
            # logger.debug(f"TOKENS DIFF: {tokens}@{result.usage.total_tokens}")
            # usage.expire()
            return result
        else:
            logger.debug(f"Tokens exceed [{request.custom_id}]")
            raise GptRateLimitException()

    async def send_without_tracking(self, request: BatchInputRequest) -> BatchInputResponse:
        logger.debug("Sending GPT Request")
        try:
            result = await self._client.chat.completions.create(
                **request.body.dict(), extra_headers={'custom_id': request.custom_id},
            )
            fin_timestamp = int(time.time())
            result_with_fin = BatchInputResponse.from_obj(result, finished=fin_timestamp)
            logger.debug("Received GPT Response")
        except RateLimitError as e:
            logger.warning(f"Rate Limit error: {e}")
            raise GptRateLimitException()
        except Exception as e:
            logger.error(f"GPT request failed {e}")
            raise GptGatewayException(e)
        return result_with_fin
