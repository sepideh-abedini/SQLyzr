import os
from typing import IO

from openai import Client
from openai.pagination import SyncCursorPage
from openai.types import FilePurpose, FileObject, Batch


class GptBatchClient:
    __gpt: Client

    def __init__(self):
        self.__gpt = Client(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=5
        )

    def create_file(self, name: str, file: IO[bytes], purpose: FilePurpose) -> FileObject:
        result = self.__gpt.files.create(
            file=(name, file),
            purpose=purpose
        )
        return result

    def list_files(self):
        result = self.__gpt.files.list()
        return result.to_json()

    def delete_file(self, file_id: str):
        result = self.__gpt.files.delete(file_id)
        return result.to_json()

    def list_batches(self) -> SyncCursorPage[Batch]:
        result = self.__gpt.batches.list()
        return result

    def create_batch(self, file_id: str) -> Batch:
        result = self.__gpt.batches.create(input_file_id=file_id, endpoint="/v1/chat/completions",
                                           completion_window="24h")
        return result

    def cancel_batch(self, batch_id: str):
        result = self.__gpt.batches.cancel(batch_id)
        return result.to_json()

    def retrieve_batch(self, batch_id: str) -> Batch:
        result = self.__gpt.batches.retrieve(batch_id)
        return result

    def retrieve_file_content(self, file_id: str) -> str:
        file_info = self.__gpt.files.retrieve(file_id)
        content = self.__gpt.files.retrieve_content(file_id)
        return content
