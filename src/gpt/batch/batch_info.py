import os
from typing import Literal, Optional

BatchInfoProps = Literal["fid", "bid", "oid"]


class BatchInfo:
    in_path: str

    def __init__(self, in_path: str):
        self.in_path = in_path

    def __file_path(self, key: BatchInfoProps):
        return f"{self.in_path}.{key}"

    def get_value(self, key: BatchInfoProps):
        if os.path.exists(self.__file_path(key)):
            with open(self.__file_path(key)) as file:
                return file.read()
        else:
            return None

    def set_value(self, key: BatchInfoProps, value: Optional[str]):
        if not value:
            if os.path.exists(self.__file_path(key)):
                os.remove(self.__file_path(key))
        else:
            with open(self.__file_path(key), "w") as file:
                file.write(value)
