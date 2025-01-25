from pydantic import BaseModel


class FileSenderUsage(BaseModel):
    total_time: float
    total_tokens: int

    @staticmethod
    def read_file(path: str):
        with open(path) as file:
            return FileSenderUsage.model_validate_json(file.read())
