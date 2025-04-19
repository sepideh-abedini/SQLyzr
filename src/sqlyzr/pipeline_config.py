from pydantic import BaseModel


class PipelineConfig(BaseModel):
    verify: bool = True
    predict: bool = True
    eval: bool = True,
    transformers: bool = True,
    augment: bool = True

    def __str__(self):
        return " ".join([
            name for name, value in self.__dict__.items() if value is True
        ])
