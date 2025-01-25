import json
import os
from abc import ABC, abstractmethod

from openai.types.chat import ChatCompletion

from src.gpt.file_sender.file_sender_usage import FileSenderUsage
from src.util.logger import debug_log
from src.util.model_utils import write_jsonl


class GptFileSender(ABC):
    _total_tokens: int
    _total_time: int

    def __init__(self):
        self._total_tokens = 0
        self._total_time = 0

    async def send_and_save(self, in_path: str, out_path: str) -> FileSenderUsage:
        debug_log(f"Asking GPT {in_path} ==> {out_path}")
        if os.path.exists(out_path):
            debug_log(f"Output path exists: {out_path}, skip asking gpt.")
            return self.__load_usage(out_path)
        responses = await self._send_file(in_path)
        write_jsonl(responses, out_path)
        usage = self.__save_usage(out_path)
        return usage

    def __save_usage(self, out_path: str):
        usage = FileSenderUsage.model_validate({'total_tokens': self._total_tokens, 'total_time': self._total_time})
        with open(self.__get_usage_path(out_path), 'w') as file:
            file.write(json.dumps(usage.dict(), indent=4))
        return usage

    @staticmethod
    def __get_usage_path(out_path: str):
        return f"{out_path}.usage.json"

    @staticmethod
    def __load_usage(out_path: str):
        return FileSenderUsage.read_file(GptFileSender.__get_usage_path(out_path))

    @abstractmethod
    async def _send_file(self, in_path: str) -> list[ChatCompletion]:
        pass
