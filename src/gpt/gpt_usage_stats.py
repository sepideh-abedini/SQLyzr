from dataclasses import dataclass, replace


@dataclass
class GptUsageStats:
    total_time: int = 0
    total_tokens: int = 0

    def __add__(self, other):
        if not isinstance(other, GptUsageStats):
            raise RuntimeError("Invalid operand type")
        return replace(
            self, total_time=self.total_time + other.total_time,
            total_tokens=self.total_tokens + other.total_tokens
        )
