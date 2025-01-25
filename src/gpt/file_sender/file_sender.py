import json
import os
from abc import ABC, abstractmethod
from typing import Optional

from openai.types.chat import ChatCompletion

from src.gpt.file_sender.usage_tracker import UsageTracker
from src.sqlyzr.file_sender_usage import FileGeneratorUsage
from src.util.logger import debug_log
from src.util.model_utils import write_jsonl


class GptFileSender(ABC):
    _tracker: Optional[UsageTracker] = None

    async def send_and_save(self, in_path: str, out_path: str) -> FileGeneratorUsage:
        debug_log(f"Asking GPT {in_path} ==> {out_path}")
        self._tracker = UsageTracker(out_path)
        if os.path.exists(out_path):
            debug_log(f"Output path exists: {out_path}, skip asking gpt.")
            return self._tracker.load_usage()
        responses = await self._send_file(in_path)
        write_jsonl(responses, out_path)
        usage = self._tracker.save_usage()
        return usage

    @abstractmethod
    async def _send_file(self, in_path: str) -> list[ChatCompletion]:
        pass
