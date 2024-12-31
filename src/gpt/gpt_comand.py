from abc import ABC, abstractmethod

from openai import NotFoundError, APIError

from src.gpt.gpt_client import GptClient


class CommandException(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)


class GptCliCommand(ABC):
    gpt_client = GptClient()

    @abstractmethod
    def __init__(self, *args):
        pass

    def execute(self):
        try:
            return self.execute_internal()
        except APIError as e:
            print(f"GPT API Error:\n{e}\n")
            raise CommandException(f"Command execution failed due to API error!")

    @abstractmethod
    def execute_internal(self):
        pass


class DeleteFile(GptCliCommand):

    def __init__(self, *args):
        if len(args) != 1:
            raise CommandException("Expected one argument: file_id")
        self.file_id = args[0]

    def execute_internal(self):
        self.gpt_client.delete_file(self.file_id)


class ListFiles(GptCliCommand):
    def __init__(self, *args):
        if len(args) > 0:
            raise CommandException("No args expected!")

    def execute_internal(self):
        return self.gpt_client.list_files()
