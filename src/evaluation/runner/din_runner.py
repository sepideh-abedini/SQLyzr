from src.evaluation.configs import EVAL_CONF
from src.evaluation.runner.model_runner import ModelRunner
from src.evaluation.runner.runner_config import SingleRunConfig
from src.third_party.din.din import run_din


class DinRunner(ModelRunner):
    def run_model(self):
        run_din(input_path=self.config.dataset_config.get_data_path(),
                output_path=self.config.get_pred_path(),
                tables_path=self.config.dataset_config.get_tables_path(),
                temp=self.config.temp)


if __name__ == "__main__":
    runner = DinRunner(EVAL_CONF.get_runner_conf(0.0, 0))
    runner.run()
