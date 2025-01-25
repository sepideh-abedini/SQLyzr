from typing import Type, TypeVar

from pydantic import BaseModel

from src.gpt.gateway.gpt_gateway import GptGateway
from src.gpt.models import BatchInputRequest
from src.util.logger import debug_log

T = TypeVar('T', bound=BaseModel)


class FormattedGptGateway(GptGateway):
    response_format: Type[T]

    def __init__(self, response_format: Type[T]):
        super().__init__()
        self.response_format = response_format

    async def _send_without_tracking(self, request: BatchInputRequest) -> T:
        debug_log("Sending formatted GPT Request")
        result = await self.__client.beta.chat.completions.parse(
            response_format=self.response_format,
            **request.body.dict()
        )
        debug_log("Received formatted GPT Response")
        return result
