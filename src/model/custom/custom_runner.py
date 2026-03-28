from src.eval.single_run_config import SingleRunConfig
from src.model.custom.custom_predictor_impl import CustomPredictorImpl
from src.sqlyzr.model_runner import ModelRunner


class CustomRunner(ModelRunner):
    async def run_single_internal(self, run_conf: SingleRunConfig):
        predictor = CustomPredictorImpl(run_conf)
        result = await predictor.run()
        return result
