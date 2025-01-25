from src.gpt.file_sender.file_sender_usage import FileSenderUsage
from src.util.model_utils import write_model, read_model


class UsageTracker:
    __total_tokens: int
    __total_time: int
    __file_path: str

    def __init__(self, file_path: str):
        self.__file_path = file_path
        self.__total_time = 0
        self.__total_tokens = 0

    @property
    def usage_path(self):
        return f"{self.__file_path}.usage.json"

    def add_time(self, time: float):
        self.__total_time += time

    def add_tokens(self, tokens: int):
        self.__total_tokens += tokens

    def save_usage(self):
        usage = FileSenderUsage.model_validate({'total_tokens': self.__total_tokens, 'total_time': self.__total_time})
        write_model(usage, self.usage_path)
        return usage

    def load_usage(self):
        return read_model(self.usage_path, FileSenderUsage)
