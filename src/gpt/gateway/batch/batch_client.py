import os
from datetime import datetime
from typing import IO, List

from openai import Client
from openai.pagination import SyncCursorPage
from openai.types import FilePurpose, FileObject, Batch


class GptBatchClient:
    __client: Client

    def __init__(self):
        self.__client = Client(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=int(os.getenv("OPENAI_TIMEOUT", 60))
        )

    def create_file(self, name: str, file: IO[bytes], purpose: FilePurpose) -> FileObject:
        result = self.__client.files.create(
            file=(name, file),
            purpose=purpose
        )
        return result

    def list_files(self):
        result = self.__client.files.list()
        return result.to_json()

    def delete_file(self, file_id: str):
        result = self.__client.files.delete(file_id)
        return result.to_json()

    def list_batches(self) -> SyncCursorPage[Batch]:
        result = self.__client.batches.list(limit=100)
        return result

    def list_cur_batches(self) -> List[Batch]:
        page = self.list_batches()
        cur_data = []
        finished = False
        while not finished:
            data = page.data
            for d in data:
                expires_at = datetime.utcfromtimestamp(d.expires_at)
                if expires_at < datetime.utcnow():
                    finished = True
                    break
                cur_data.append(d)
            if page.has_next_page():
                page = page.get_next_page()
            else:
                break
        return cur_data

    def create_batch(self, file_id: str) -> Batch:
        result = self.__client.batches.create(input_file_id=file_id, endpoint="/v1/chat/completions",
                                              completion_window="24h")
        print(f"Batch created: {result.status}")
        return result

    def cancel_batch(self, batch_id: str):
        result = self.__client.batches.cancel(batch_id)
        return result.to_json()

    def retrieve_batch(self, batch_id: str) -> Batch:
        result = self.__client.batches.retrieve(batch_id)
        return result

    def retrieve_file_content(self, file_id: str) -> str:
        file_info = self.__client.files.retrieve(file_id)
        content = self.__client.files.retrieve_content(file_id)
        return content
