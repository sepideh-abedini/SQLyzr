import os
from dataclasses import dataclass, field
from itertools import product
from typing import List, Dict, Type
from src.eval.dataset_config import DatasetConfig
from src.eval.metrics import Metric
from src.eval.single_run_config import SingleRunConfig, ModelName
from src.sqlyzr.chart_config import PlotName

DEFAULT_TEMP = 0.2


@dataclass
class ModelEvalConfig:
    run_confs: Dict[float, List[SingleRunConfig]]
    base_dir: str
    eval_dir: str
    pred_dir: str
    trs_dir: str
    charts_dir: str
    included_charts: List[PlotName]
    dataset_configs: List[DatasetConfig]
    metrics: Dict[str, Type[Metric]]
    scales: List[int]
    options: Dict = field(default_factory=dict)

    @staticmethod
    def create(temps: List[float], num_itrs: int, pred_dir: str, eval_dir: str, trs_dir: str, charts_dir: str,
               base_dir: str,
               dataset_configs: List[DatasetConfig],
               metrics: Dict[str, Type[Metric]],
               included_charts: List[PlotName],
               models: List[ModelName],
               batch: bool,
               scales: List[int],
               options: Dict[str, str]):
        run_confs = {}
        if len(temps) == 0:
            temps = [DEFAULT_TEMP]
        for model in models:
            for temp, itr in product(temps, range(num_itrs)):
                for dataset_config in dataset_configs:
                    conf = SingleRunConfig(dataset_config=dataset_config,
                                           pred_dir=pred_dir,
                                           trs_dir=trs_dir,
                                           eval_dir=eval_dir,
                                           temp=temp,
                                           itr=itr,
                                           batch=batch,
                                           model=model,
                                           scales=scales,
                                           options=options)
                    run_confs.setdefault(temp, []).append(conf)
        return ModelEvalConfig(
            run_confs=run_confs,
            base_dir=base_dir,
            eval_dir=eval_dir,
            pred_dir=pred_dir,
            trs_dir=trs_dir,
            charts_dir=charts_dir,
            included_charts=included_charts,
            dataset_configs=dataset_configs,
            metrics=metrics,
            scales=scales
        )

    @property
    def models(self):
        return set(map(lambda conf: conf.model, self.get_run_confs()))

    @property
    def datasets(self):
        return set(map(lambda conf: conf.dataset_type, self.dataset_configs))

    def get_run_confs(self):
        return list([conf for ll in self.run_confs.values() for conf in ll])

    def get_runner_conf(self, temp: float, itr: int):
        return self.run_confs[temp][itr]

    def get_raw_scores_path(self):
        return os.path.join(self.eval_dir, f"scores_raw.csv")

    def get_scores_path(self, sub: str = ""):
        return os.path.join(self.eval_dir, f"scores{sub}.csv")

    def get_metric_names(self):
        return list(self.metrics.keys())
