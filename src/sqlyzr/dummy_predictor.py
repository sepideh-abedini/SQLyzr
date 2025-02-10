from src.pred.predictor import Predictor, load_data


class DummyPredictor(Predictor):
    async def _run_internal(self):
        self._tracker.start()
        examples = load_data(self._run_conf.dataset_config.get_data_path()).to_dict("records")
        with open(self._run_conf.get_pred_path(), "w") as file:
            for i, example in enumerate(examples):
                sql = example['query']
                file.write(f"{sql}\n")
        self._tracker.lap_time()
