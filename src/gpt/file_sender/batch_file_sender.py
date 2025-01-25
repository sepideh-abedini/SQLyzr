import asyncio
import os
from abc import ABC, abstractmethod
from typing import List, Type, TypeVar

from openai.types import Batch
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from src.gpt.batch.batch_gateway import GptBatchGateway
from src.gpt.file_sender.file_sender import GptFileSender
from src.gpt.gpt_gateway import GptGateway, FormattedGptGateway
from src.gpt.gpt_usage_stats import GptUsageStats
from src.gpt.models import BatchInputRequest, SqlyzrChatCompletion
from src.util.logger import log, debug_log


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
