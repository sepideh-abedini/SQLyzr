import pandas as pd
from loguru import logger

from src.cat.categories import find_cat
from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.lib import confidence_interval
from src.util.log_util import log


def metric_consistency(metric):
    def agg_fun(grouped):
        ea = grouped['ea']
        ms = grouped[metric]
        den = ea.sum()
        if den == 0:
            return 0.0
        return (ea & ms).sum() / den

    return agg_fun


def metric_agg(metric, agg_fun):
    return pd.NamedAgg(column=metric, aggfunc=agg_fun)


METRICS = [
    "em", "ea", "rea", "et", "get"
]

SUMS = {
    f"{m}_sum": pd.NamedAgg(column=m, aggfunc="sum") for m in METRICS
}

MEANS = {
    f"{m}_mean": pd.NamedAgg(column=m, aggfunc="mean") for m in METRICS
}

CIS = {
    f"{m}_ci": pd.NamedAgg(column=m, aggfunc=confidence_interval) for m in METRICS
}


class ScoresPostProcessor:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    @log("Score post-processing")
    def run(self):
        config = self.__config.eval_conf
        df = pd.read_csv(config.get_raw_scores_path(), index_col=0)
        df = df.drop(columns=['pcat', 'psub', 'dst', 'itr'])

        sub_grouped = df.groupby(['tmp', 'cat', 'sub'])
        cc = sub_grouped.apply(metric_consistency('plc'))
        etc = sub_grouped.apply(metric_consistency('plt'))
        sub_grouped = sub_grouped.agg(**SUMS, **MEANS, **CIS)
        sub_grouped['cc'] = cc
        sub_grouped['etc'] = etc
        sub_grouped = sub_grouped.reset_index()
        sub_grouped.to_csv(config.get_scores_path("_sub"))
        logger.info(f"Sub grouped cols: {len(sub_grouped.columns)}")

        cat_grouped = df.drop(columns=['sub']).groupby(['tmp', 'cat'])
        cc = cat_grouped.apply(metric_consistency('plc'))
        etc = cat_grouped.apply(metric_consistency('plt'))
        cat_grouped = cat_grouped.agg(**MEANS, **SUMS, **CIS)
        cat_grouped['cc'] = cc
        cat_grouped['etc'] = etc
        cat_grouped['sub'] = 'all'
        cat_grouped = cat_grouped.reset_index()
        cat_grouped.to_csv(config.get_scores_path("_cat"))
        logger.info(f"sub = all  cols: {len(cat_grouped.columns)}")

        tmp_cat_grouped = df.drop(columns=['sub']).groupby(['tmp', 'cat'])
        cc = tmp_cat_grouped.apply(metric_consistency('plc'))
        etc = tmp_cat_grouped.apply(metric_consistency('plt'))
        tmp_cat_grouped = tmp_cat_grouped.mean()
        tmp_cat_grouped['cc'] = cc
        tmp_cat_grouped['etc'] = etc
        tmp_cat_grouped = tmp_cat_grouped.reset_index()
        all_cats = tmp_cat_grouped.drop(columns=['cat']).groupby(['tmp'])
        all_cats = all_cats.agg(**SUMS, **MEANS, **CIS, cc=pd.NamedAgg(column="cc", aggfunc="mean"),
                                etc=pd.NamedAgg(column="etc", aggfunc="mean"))
        all_cats['cat'] = 'all'
        all_cats['sub'] = 'all'
        all_cats = all_cats.reset_index()
        all_cats.to_csv(config.get_scores_path("_all"))
        logger.info(f"cat = all cols: {len(all_cats.columns)}")

        combined = pd.concat([sub_grouped, cat_grouped, all_cats], ignore_index=True)
        combined.to_csv(config.get_scores_path("_combined"))
        final = combined.copy()
        final = final.round(2)
        final.to_csv(config.get_scores_path())
