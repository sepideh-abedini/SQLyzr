import os.path
from abc import ABC, abstractmethod
from pathlib import Path

from openai import NotFoundError, APIError
from pydantic import ValidationError

from src.gpt.gpt_client import GptBatchClient
from src.gpt.models import BatchInputRequest


class CommandException(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)


class GptCliCommand(ABC):
    gpt_client = GptBatchClient()

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
        return self.gpt_client.delete_file(self.file_id)


class ListFiles(GptCliCommand):
    def __init__(self, *args):
        if len(args) > 0:
            raise CommandException("No args expected!")

    def execute_internal(self):
        return self.gpt_client.list_files()


class CreateFile(GptCliCommand):
    file_path: str

    def __init__(self, *args):
        if len(args) != 1:
            raise CommandException("Expected one arg: file_path")
        self.file_path = args[0]

    def execute_internal(self):
        self.validate_file()
        file = open(self.file_path, "rb")
        file_name = os.path.basename(self.file_path)
        return self.gpt_client.create_file(file_name, file, "batch")

    def validate_file(self):
        path = Path(self.file_path)
        if not path.exists():
            raise CommandException(f"File not exists!: {self.file_path}")
        if path.is_dir():
            raise CommandException(f"Is a dir!: {self.file_path}")
        file = open(self.file_path)
        for i, line in enumerate(file.readlines()):
            try:
                BatchInputRequest.model_validate_json(line)
            except ValidationError as v:
                print(v)
                raise CommandException(f"Invalid line {self.file_path}:{i + 1}")


class ListBatches(GptCliCommand):
    def __init__(self, *args):
        if len(args) > 0:
            raise CommandException("No args expected!")

    def execute_internal(self):
        all_data = []
        page = self.gpt_client.list_batches()
        for entry in page.data:
            print(f"{entry.id}: {entry.status} {entry.errors}")


class CreateBatch(GptCliCommand):
    def __init__(self, *args):
        if len(args) != 1:
            raise CommandException("Expected one argument: file_id")
        self.file_id = args[0]

    def execute_internal(self):
        return self.gpt_client.create_batch(self.file_id)


class DeleteBatch(GptCliCommand):
    def __init__(self, *args):
        if len(args) != 1:
            raise CommandException("Expected one argument: batch_id")
        self.batch_id = args[0]

    def execute_internal(self):
        return self.gpt_client.cancel_batch(self.batch_id)


class RetrieveBatch(GptCliCommand):
    def __init__(self, *args):
        if len(args) != 1:
            raise CommandException("Expected one argument: batch_id")
        self.batch_id = args[0]

    def execute_internal(self):
        return self.gpt_client.retrieve_batch(self.batch_id)


class RetrieveFileContent(GptCliCommand):
    def __init__(self, *args):
        if len(args) != 1:
            raise CommandException("Expected one argument: file_id")
        self.file_id = args[0]

    def execute_internal(self):
        return self.gpt_client.retrieve_file_content(self.file_id)
