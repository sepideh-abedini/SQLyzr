from src.sqlyzr.file_sender_usage import FileGeneratorUsage
from src.util.model_utils import write_model, read_model


class UsageTracker:
    __usage: FileGeneratorUsage
    __file_path: str

    def __init__(self, file_path: str):
        self.__file_path = file_path
        self.__usage = FileGeneratorUsage()

    @property
    def usage_path(self):
        return f"{self.__file_path}.usage.json"

    def add_time(self, time: float):
        self.__usage = self.__usage.plus_time(time)

    def add_tokens(self, tokens: int):
        self.__usage = self.__usage.plus_tokens(tokens)

    def add_usage(self, usage: FileGeneratorUsage):
        self.__usage += usage

    def save_usage(self):
        write_model(self.__usage, self.usage_path)
        return self.__usage

    def load_usage(self) -> FileGeneratorUsage:
        self.__usage = read_model(self.usage_path, FileGeneratorUsage)
        return self.__usage
