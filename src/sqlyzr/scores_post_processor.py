import pandas as pd

from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.lib import confidence_level_interval
from src.util.log_util import log

AGG_FUNS = {
    'sum': 'sum',
    'mean': 'mean',
    'ci': confidence_level_interval
}

SCORES_AGGS = {
    'ea': ['sum', 'mean', 'ci'],
    'em': ['sum', 'mean', 'ci'],
    'rea': ['sum', 'mean', 'ci'],
}

aggs = dict()
for s, sa in SCORES_AGGS.items():
    for a in sa:
        aggs[f"{s}_{a}"] = pd.NamedAgg(column=s, aggfunc=AGG_FUNS[a])


class ScoresPostProcessor:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    @staticmethod
    def metric_consistency(metric):
        def agg_fun(grouped):
            ea = grouped['ea']
            ms = grouped[metric]
            den = ea.sum()
            if den == 0:
                return 0.0
            return (ea & ms).sum() / den

        return agg_fun

    @log("Score post-processing")
    def run(self):
        config = self.__config.eval_conf
        df = pd.read_csv(config.get_raw_scores_path(), index_col=0)
        df['count'] = 1

        cat_grouped = df.groupby(['tmp', 'cat'])
        cat_grouped = cat_grouped.agg(**aggs)
        cat_grouped['sub'] = 'all'
        cat_grouped.to_csv(config.get_scores_path("_cat"))

        # sub_grouped = df.groupby(['tmp', 'cat', 'sub'])
        # sub_grouped = sub_grouped.reset_index()
        # sub_grouped.to_csv(config.get_scores_path("_sub"))
        # cat_grouped = df.groupby(['tmp', 'cat'])

        # aggs = dict()
        #
        # metric_names = config.get_metric_names()
        # metric_names.append('count')
        #
        # for m in metric_names:
        #     aggs[f"{m}_sum"] = pd.NamedAgg(column=m, aggfunc='sum')
        #     aggs[f"{m}_mean"] = pd.NamedAgg(column=m, aggfunc='mean')
        #     aggs[f"{m}_ci"] = pd.NamedAgg(column=m, aggfunc=confidence_level_interval)
        # df_subcat_grouped = df.groupby(['tmp', 'cat', 'sub_cat'])
        # cc = df_subcat_grouped.apply(ScoresPostProcessor.metric_consistency('cc'))
        # etc = df_subcat_grouped.apply(ScoresPostProcessor.metric_consistency('etc'))
        # df_subcat = df.groupby(['tmp', 'cat', "sub_cat"]).agg(
        #     **aggs
        # )
        # df_subcat = df_subcat.reset_index()
        # df_subcat['cc_mean'] = cc.values
        # df_subcat['etc_mean'] = etc.values
        # df_subcat.to_csv(config.get_scores_path("_cat_subcat"))
        #
        # df_cat = df.groupby(['tmp', 'cat']).agg(
        #     **aggs
        # )
        # df_cat['sub_cat'] = 'all'
        # df_cat = df_cat.reset_index()
        # df_cat.to_csv(config.get_scores_path("_cat"))
        # cat_means = df_cat[['ea_mean', 'rea_mean', 'etc_mean', 'cc_mean', 'em_mean']].groupby(['tmp']).mean()
        #
        # df_all = df.groupby(['tmp']).agg(
        #     **aggs
        # )
        # df_all['sub_cat'] = 'all'
        # df_all['cat'] = 'all'
        # df_all = df_all.reset_index()
        # df_all.to_csv(config.get_scores_path("_all"))
        #
        # combined = pd.concat([df_subcat, df_cat, df_all], ignore_index=True)
        # combined.to_csv(config.get_scores_path("_combined"))
        # final = combined.copy()
        # final = final.round(2)
        # final.to_csv(config.get_scores_path())
