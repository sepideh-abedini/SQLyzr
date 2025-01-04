import os
from typing import TypeVar, Type

import backoff
from openai import AsyncClient
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from src.gpt.gpt_tracker import GptUsageTracker
from src.gpt.models import BatchInputRequest


class GptGatewayException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class GptRateLimitException(GptGatewayException):
    def __init__(self):
        super().__init__("Token limit hit!")


class GptBatchNotCompletedException(GptGatewayException):
    def __init__(self):
        super().__init__("Batch not completed exception")


class GptBatchFailedException(GptGatewayException):
    def __init__(self, msg):
        super().__init__(msg)


class GptGateway:
    client: AsyncClient
    tracker: GptUsageTracker

    def __init__(self):
        self.client = AsyncClient(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=5
        )
        self.tracker = GptUsageTracker.get_instance()

    async def send_without_tracking(self, request: BatchInputRequest) -> ChatCompletion:
        print("Sending GPT Request")
        result = await self.client.chat.completions.create(
            **request.body.dict()
        )
        print("Received GPT Response")
        return result

    @backoff.on_exception(backoff.constant, interval=10, max_tries=5, exception=GptRateLimitException)
    async def track_and_send(self, request: BatchInputRequest):
        print(f"Sending [{request.custom_id}]")
        tokens = request.get_token_usage()
        can_send = await self.tracker.check_limit(tokens)
        if can_send:
            usage = await self.tracker.add_usage(tokens)
            result = await self.send_without_tracking(request)
            usage.expire()
            return result
        else:
            raise GptRateLimitException()


T = TypeVar('T', bound=BaseModel)


class FormattedGptGateway(GptGateway):
    response_format: Type[T]

    def __init__(self, response_format: Type[T]):
        super().__init__()
        self.response_format = response_format

    async def send_without_tracking(self, request: BatchInputRequest) -> T:
        print("Sending formatted GPT Request")
        result = await self.client.beta.chat.completions.parse(
            response_format=self.response_format,
            **request.body.dict()
        )
        print("Received formatted GPT Response")
        return result
