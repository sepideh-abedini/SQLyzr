from typing import List

from src.pred.predictor import Predictor, load_data


class DummyPredictor(Predictor):
    def get_out_batch_files(self) -> List[str]:
        pass

    def save_tokens(self):
        examples = load_data(self._run_conf.dataset_config.get_test_path()).to_dict("records")
        with open(self._run_conf.get_tokens_path(), "w") as tok_file:
            tok_file.write("\n".join([str(1000)] * len(examples)))

    async def _run_internal(self):
        examples = load_data(self._run_conf.dataset_config.get_test_path()).to_dict("records")
        with open(self._run_conf.get_pred_path(), "w") as file:
            for i, example in enumerate(examples):
                sql = example['query']
                file.write(f"{sql}\n")
