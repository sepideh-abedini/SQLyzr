from typing import Type, TypeVar

from pydantic import BaseModel

from src.gpt.gateway.gateway import GptGateway
from src.gpt.models import BatchInputRequest

from loguru import logger

T = TypeVar('T', bound=BaseModel)


class FormattedGptGateway(GptGateway):
    response_format: Type[T]

    def __init__(self, response_format: Type[T]):
        super().__init__()
        self.response_format = response_format

    async def send_without_tracking(self, request: BatchInputRequest) -> T:
        logger.debug("Sending formatted GPT Request")
        result = await self._client.beta.chat.completions.parse(
            response_format=self.response_format,
            **request.body.dict()
        )
        logger.debug("Received formatted GPT Response")
        return result
