import os
from abc import ABC, abstractmethod

from src.gpt.models import SqlyzrChatCompletion
from src.util.logger import debug_log
from src.util.model_utils import write_jsonl


class GptFileSender(ABC):
    async def send_and_save(self, in_path: str, out_path: str):
        debug_log(f"Asking GPT {in_path} ==> {out_path}")
        if os.path.exists(out_path):
            debug_log(f"Output path exists: {out_path}, skip asking gpt.")
            return
        responses = await self.send_from_file(in_path)
        write_jsonl(responses, out_path)

    @abstractmethod
    async def send_from_file(self, in_path: str) -> list[SqlyzrChatCompletion]:
        pass
