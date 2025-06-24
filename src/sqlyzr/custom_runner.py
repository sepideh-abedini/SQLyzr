from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.model_runner import ModelRunner


class CustomRunner(ModelRunner):
    async def run_single_internal(self, run_conf: SingleRunConfig):
        pass
