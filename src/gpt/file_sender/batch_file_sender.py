from typing import Type, TypeVar

from pydantic import BaseModel

from src.gpt.batch.batch_gateway import GptBatchGateway
from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.file_sender.single_file_sender import GptSingleSender
from src.gpt.gateway.formatted_gateway import FormattedGptGateway
from src.gpt.models import SqlyzrChatCompletion


class GptBatchFileSender(GptFileSender):
    gateway: GptBatchGateway

    def __init__(self):
        self.gateway = GptBatchGateway()

    async def send_from_file(self, in_path: str) -> list[SqlyzrChatCompletion]:
        output = await self.gateway.send_batch(in_path)
        result = list(map(lambda o: o.response.body, output))
        return result


T = TypeVar('T', bound=BaseModel)


class GptFormattedSingleSender(GptSingleSender):
    response_format: Type[T]

    def __init__(self, response_format: Type[T]):
        super().__init__()
        self.response_format = response_format
        self.gateway = FormattedGptGateway(response_format)
