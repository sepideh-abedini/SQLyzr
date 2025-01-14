from pydantic import BaseModel


class PipelineConfig(BaseModel):
    verify: bool = True
    predict: bool = True
    eval: bool = True,
    transformers: bool = True,
    augment: bool = True

