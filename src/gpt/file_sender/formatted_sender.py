from typing import Type, TypeVar

from pydantic import BaseModel

from src.gpt.file_sender.single_sender import GptSingleSender
from src.gpt.gateway.formatted_gateway import FormattedGptGateway

T = TypeVar('T', bound=BaseModel)


class GptFormattedSingleSender(GptSingleSender):
    response_format: Type[T]

    def __init__(self, response_format: Type[T]):
        super().__init__()
        self.response_format = response_format
        self._gateway = FormattedGptGateway(response_format)
