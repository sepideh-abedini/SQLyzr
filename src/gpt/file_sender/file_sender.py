import os
from abc import ABC, abstractmethod

from loguru import logger

from src.gpt.models import SqlyzrChatCompletion
from src.util.model_utils import write_jsonl

FORCE = bool(int(os.environ.get("FORCE", 0)))

class GptFileSender(ABC):

    async def send_and_save(self, in_path: str, out_path: str, force: bool = False) -> None:
        logger.debug(f"Asking GPT {in_path} ==> {out_path}")
        if not FORCE and os.path.exists(out_path):
            logger.debug(f"Output path exists: {out_path}, skip asking gpt.")
            return
        responses = await self._send_file(in_path)
        write_jsonl(responses, out_path)

    @abstractmethod
    async def _send_file(self, in_path: str) -> list[SqlyzrChatCompletion]:
        pass
