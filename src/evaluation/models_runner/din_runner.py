from src.evaluation.models_runner.run_config import RunConfig
from src.third_party.din.din import run_din


class DinRunner:
    def run(self, config: RunConfig):
        run_din(input_path=config.input_path,
                output_path=config.output_path,
                tables_path=config.tables_path,
                temp=config.temp)
