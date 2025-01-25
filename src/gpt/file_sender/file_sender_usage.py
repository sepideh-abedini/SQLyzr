from pydantic import BaseModel


class FileSenderUsage(BaseModel):
    total_time: float = 0
    total_tokens: int = 0

    @staticmethod
    def read_file(path: str):
        with open(path) as file:
            return FileSenderUsage.model_validate_json(file.read())

    def __add__(self, other):
        if not isinstance(other, FileSenderUsage):
            raise RuntimeError(f"Invalid operand: {other}")
        return self.model_copy(update={
            "total_tokens": self.total_tokens + other.total_tokens,
            "total_time": self.total_time + other.total_time
        })
