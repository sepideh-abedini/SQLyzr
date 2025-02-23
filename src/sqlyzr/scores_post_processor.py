import pandas as pd

from src.configs.sqlyzr import SQLyzrConfig
from src.eval.lib import confidence_level_interval
from src.gpt.file_sender.usage_tracker import ResourceUsage
from src.sqlyzr.file_sender_usage import FileGeneratorUsage
from src.util.model_utils import read_model


class ScoresPostProcessor:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    def run(self):
        config = self.__config.eval_conf
        df = pd.read_csv(config.get_raw_scores_path(), index_col=0)
        df['count'] = 1

        all_sub_cats = df.groupby(['tmp', 'itr', "cat"], as_index=False).sum()
        all_sub_cats['sub_cat'] = 'all'
        all_sub_cats.to_csv(config.get_scores_path("_all_sub_cats"))

        all_cats = df.groupby(['tmp', 'itr'], as_index=False).sum()
        all_cats['cat'] = 'all'
        all_cats['sub_cat'] = 'all'
        all_cats.to_csv(config.get_scores_path("_all_cats"))

        for run_conf in self.__config.eval_conf.get_run_confs():
            usage = read_model(run_conf.get_usage_path(), ResourceUsage)
            row_match = (all_cats['tmp'] == run_conf.temp) & (all_cats['itr'] == run_conf.itr)
            all_cats.loc[row_match, 'time'] = usage.time
            all_cats.loc[row_match, 'mem'] = usage.mem
            all_cats.loc[row_match, 'cpu'] = usage.cpu
            all_cats.loc[row_match, 'tokens'] = usage.tokens
            all_cats = all_cats.round(2)
            all_cats.to_csv(config.get_scores_path("_usage"))


        combined = pd.concat([all_cats, all_sub_cats, df], join='inner', ignore_index=True)
        combined.to_csv(config.get_scores_path("_combined"))

        sums = combined.groupby(['tmp', 'itr', 'cat', "sub_cat"], as_index=False).sum()
        sums.to_csv(config.get_scores_path("_sum"))

        metric_names = config.get_metric_names()
        means = sums.copy()
        means[metric_names] = sums[metric_names].div(sums['count'], axis=0)
        means.to_csv(config.get_scores_path("_means"), index_label="idx")

        means_per_temp = means.groupby(['tmp', 'cat', "sub_cat"]).mean()
        means_per_temp[metric_names] = means_per_temp[metric_names] * 100
        means_per_temp = means_per_temp.drop(columns=['itr'])
        means_per_temp.to_csv(config.get_scores_path("_means_per_temp"))

        cis = means.groupby(['tmp', 'cat', "sub_cat"]).agg(confidence_level_interval)
        cis = cis.drop(columns=['itr'])
        cis.to_csv(config.get_scores_path("_cis"))

        final = means_per_temp.join(cis, lsuffix="_mean", rsuffix="_ci")
        final = final.round(2)
        final.to_csv(config.get_scores_path())
