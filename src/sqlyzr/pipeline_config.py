from pydantic import BaseModel


class PipelineConfig(BaseModel):
    verify: bool = False
    predict: bool = False
    eval: bool = False,
    transformers: bool = False,
    augment: bool = False
    charts: bool = False

    def __str__(self):
        return " ".join([
            name for name, value in self.__dict__.items() if value is True
        ])
