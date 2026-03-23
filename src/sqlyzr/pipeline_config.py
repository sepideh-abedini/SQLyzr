import os

from pydantic import BaseModel

SQLYZR_PIPELINE_STATUS_PATH = "/tmp/sqlyzr_status.json"


class PipelineConfig(BaseModel):
    verify: bool = False
    predict: bool = False
    eval: bool = False
    analysis: bool = False
    augment: bool = False
    plots: bool = False
    scale: bool = False

    def __str__(self):
        return " ".join([
            name for name, value in self.__dict__.items() if value is True
        ])

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        self.save()

    def save(self):
        with open(SQLYZR_PIPELINE_STATUS_PATH, "w") as out_file:
            out_file.write(self.model_dump_json(indent=4))
        return self

    @staticmethod
    def init():
        return PipelineConfig().save()
