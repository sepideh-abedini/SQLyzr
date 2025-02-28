import pandas as pd

from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.lib import confidence_level_interval
from src.gpt.file_sender.usage_tracker import ResourceUsage
from src.util.model_utils import read_model


class ScoresPostProcessor:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    def run(self):
        config = self.__config.eval_conf
        df = pd.read_csv(config.get_raw_scores_path(), index_col=0)
        df['count'] = 1

        aggs = dict()

        metric_names = config.get_metric_names()
        metric_names.append('count')

        for m in metric_names:
            aggs[f"{m}_sum"] = pd.NamedAgg(column=m, aggfunc='sum')
            aggs[f"{m}_mean"] = pd.NamedAgg(column=m, aggfunc='mean')
            aggs[f"{m}_ci"] = pd.NamedAgg(column=m, aggfunc=confidence_level_interval)
        df_cat_subcat = df.groupby(['tmp', 'cat', "sub_cat"]).agg(
            **aggs
        )
        df_cat_subcat = df_cat_subcat.reset_index()
        df_cat_subcat.to_csv(config.get_scores_path("_cat_subcat"))

        df_cat = df.groupby(['tmp', 'cat']).agg(
            **aggs
        )
        df_cat['sub_cat'] = 'all'
        df_cat = df_cat.reset_index()
        df_cat.to_csv(config.get_scores_path("_cat"))

        df_all = df.groupby(['tmp']).agg(
            **aggs
        )
        df_all['sub_cat'] = 'all'
        df_all['cat'] = 'all'
        df_all = df_all.reset_index()
        df_all.to_csv(config.get_scores_path("_all"))

        combined = pd.concat([df_cat_subcat, df_cat, df_all], ignore_index=True)
        combined.to_csv(config.get_scores_path("_combined"))

        # for run_conf in self.__config.eval_conf.get_run_confs():
        #     usage = read_model(run_conf.get_usage_path(), ResourceUsage)
        #     row_match = (df_all['tmp'] == run_conf.temp) & (df_all['itr'] == run_conf.itr)
        #     df_all.loc[row_match, 'time'] = usage.time
        #     df_all.loc[row_match, 'mem'] = usage.mem
        #     df_all.loc[row_match, 'cpu'] = usage.cpu
        #     df_all.loc[row_match, 'tokens'] = usage.tokens
        #     df_all = df_all.round(2)
        #     df_all.to_csv(config.get_scores_path("_usage"))

        #
        final = combined.copy()
        # final = means_per_temp.join(cis, lsuffix="_mean", rsuffix="_ci")
        final = final.round(2)
        final.to_csv(config.get_scores_path())
