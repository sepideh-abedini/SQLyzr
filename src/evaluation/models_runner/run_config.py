from dataclasses import dataclass


@dataclass
class RunConfig:
    input_path: str
    output_path: str
    tables_path: str
    temp: float
