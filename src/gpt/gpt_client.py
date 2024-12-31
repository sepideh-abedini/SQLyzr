import os
from typing import IO

from openai import Client
from openai.types import FilePurpose


class GptClient:
    __gpt: Client

    def __init__(self):
        self.__gpt = Client(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=5
        )

    def create_file(self, name: str, file: IO[bytes], purpose: FilePurpose):
        result = self.__gpt.files.create(
            file=(name, file),
            purpose=purpose
        )
        return result.to_json()

    def list_files(self):
        result = self.__gpt.files.list()
        return result.to_json()

    def delete_file(self, file_id: str):
        result = self.__gpt.files.delete(file_id)
        return result.to_json()
