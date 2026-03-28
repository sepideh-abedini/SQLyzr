import os.path
from typing import Optional

from loguru import logger

import pandas as pd
import seaborn as sns
from dataclasses_json.stringcase import snakecase
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.transforms import Bbox
from natsort import natsorted
from pandas import DataFrame

SHOW_ERROR_BAR = True

FIG_HEIGHT = 5
BAR_WIDTH = 0.8

# plt.rcParams["font.size"] = 24
# plt.rcParams["font.weight"] = "bold"
# plt.rcParams["lines.linewidth"] = 3
# plt.rcParams["legend.fontsize"] = 8
# plt.rcParams['legend.title_fontsize'] = 16
#
ET_TRESH = 0.1
INCLUDE_ALL = True


def fix_plot_size(df: pd.DataFrame, x: str, hue: str, scale=1):
    num_x = len(df[x].unique())
    num_h = len(df[hue].unique())
    base_width = num_x
    width = (base_width * max(scale, num_h / 2))
    plt.title("Overall Scores")
    col_width = 0.8
    if num_h > 1:
        col_width = (col_width / (width / base_width)) * (num_h / 2)
    else:
        col_width = (col_width / (width / base_width))
    plt.figure(figsize=(width, FIG_HEIGHT))
    return col_width


COL_NAMES = {
    "ea": "Execution Accuracy",
    "rea": "Relaxed Execution Accuracy",
    "em": "Exact Match",
    "sem": "Spider Exact Match",
    "et": "Execution Time",
    "get": "Gold Execution Time",
    "etc": "Execution Time Consistency",
    "cconst": "Complexity Consistency",
    "tokens": "Token Usage",
    "cat": "Category",
    "sub": "SubCategory",
    "cdiff": "Complexity Inconsistency",
    "etcdiff": "Execution Time Inconsistency",
    "model": "Model",
    "dst": "Dataset",
    "tmp": "Temp",
    "dst_ver": "Workload Version"
}

custom_palette = ["#1f77b4", "#ff7f0e"]
bar_width = 0.8
bar_spacing = 0.2
height = 5


def full_extent(ax, pad=0.0):
    """Get the full extent of an axes, including axes labels, tick labels, and
    titles."""
    # For text objects, we need to draw the figure first, otherwise the extents
    # are undefined.
    ax.figure.canvas.draw()
    items = ax.get_xticklabels() + ax.get_yticklabels()
    #    items += [ax, ax.title, ax.xaxis.label, ax.yaxis.label]
    items += [ax, ax.title]
    bbox = Bbox.union([item.get_window_extent() for item in items])
    return bbox.expanded(1.0 + pad, 1.0 + pad)


def melt_scores(df):
    df = pd.melt(df, id_vars=["Model", 'Dataset', 'Category', 'Temp', 'SubCategory', 'Workload Version'],
                 value_vars=['Execution Accuracy',
                             # 'Relaxed Execution Accuracy',
                             'Exact Match',
                             'Complexity Consistency', "Execution Time Consistency"],
                 var_name="Metric",
                 value_name="Score")

    return df


OUT_DIR = "charts"


class Drawer:
    include_all: bool
    only_correct: bool
    exclude_c6: bool
    df: DataFrame
    hue: str

    def __init__(self, scores_path: str, include_all: bool = False, only_correct: bool = False,
                 exclude_c6: bool = False, show: bool = False, out_dir: str = OUT_DIR, hue: str = "Model"):
        self.hue = hue
        self.out_dir = out_dir
        self.show = show
        self.include_all = include_all
        self.only_correct = only_correct
        self.exclude_c6 = exclude_c6
        self.df = self.proc_df(scores_path)

    def add_overall(self, df: DataFrame, x: str):
        x = "Category"
        dst_vers = natsorted(df['Workload Version'].unique())
        to_drop = {'Category', 'SubCategory', 'Dataset'}
        to_drop = list(to_drop.difference({x}))
        # We are using raw scores, so we need this
        mean_values = df.drop(columns=to_drop).groupby(["Model", 'Workload Version', x], observed=False).mean()
        mean_values = mean_values.groupby(["Model", 'Workload Version'], observed=False).mean()
        #
        for (model, dst_ver) in df[["Model", 'Workload Version']].drop_duplicates().itertuples(index=False):
            new_row = {"Model": model, 'Workload Version': dst_ver, 'Category': "overall", "SubCategory": "overall"}
            new_row.update(mean_values.loc[(model, dst_ver)].to_dict())
            row = pd.DataFrame([new_row])
            row['Workload Version'] = pd.Categorical(row['Workload Version'], categories=dst_vers, ordered=True)
            df = pd.concat([df, row], ignore_index=True)
        return df

    def proc_df(self, scores_path: str):
        logger.info(f"Processing {scores_path}")
        df = pd.read_csv(scores_path)
        df["cat"] = df["cat"].str.upper()
        df["sub"] = df["sub"].str.upper()
        df = df.dropna(subset=["cat"])
        cats = natsorted(df['cat'].unique())
        sub_cats = natsorted(df['sub'].unique())
        dst_vers = natsorted(df['dst_ver'].unique())
        df['cat'] = pd.Categorical(df['cat'], categories=cats, ordered=True)
        df['sub'] = pd.Categorical(df['sub'], categories=sub_cats, ordered=True)
        df['dst_ver'] = pd.Categorical(df['dst_ver'], categories=dst_vers, ordered=True)
        df = df.sort_values(by=['cat', 'sub', 'dst_ver'])
        if self.only_correct:
            df = df[df['rea'] == 1]
        # df['etc'] = (df['et'] < df['get'] * (1 + ET_TRESH)).astype(int)
        # df['plt'] = df.apply(lambda e: int((e['et'] / e['get']) > 1 + ET_TRESH), axis=1)
        # df['plt'] = ((df['get'] != 0) & ((df['et'] / df['get']) > conf.etc_ratio)).astype(int)
        df['etc'] = df['plt']
        df["cconst"] = df["plc"]
        df["cdiff"] = 1 - df["plc"]
        df["etcdiff"] = 1 - df["plt"]
        df = df.drop(columns=[col for col in df.columns if "Unnamed" in col])
        df = df.drop(columns=['pcat', 'psub', 'id'], errors='ignore')
        if self.exclude_c6:
            df = df[df['cat'] != 'c6']

        tmps = df["tmp"].unique()
        if len(tmps) > 0:
            TOP_TEMP = tmps[0]
            df = df[df['tmp'] == TOP_TEMP]

        df = df.rename(columns=COL_NAMES)

        if self.hue != 'Workload Version':
            versions = df['Workload Version'].cat.categories
            last_ver = max(versions, key=lambda x: int(x[1:]))
            df = df[df['Workload Version'] == last_ver]
        # df.to_csv("charts/data.csv", index=False)
        return df

    def metric_dir(self, metric):
        return os.path.join(self.out_dir, snakecase(metric))

    def draw_barplot(self, df: DataFrame, x: str, y: str, hue: str, estimator: str):
        order = [
            's0',
            's1', 's2',
            's8', 's6', 's3', 's9', 's7', 's4', 's5',
            's16', 's17', 's13', 's19', 's12', 's11', 's14', 's15', 's18',
            's20', 's21', 's22', 's25', 's24',
            's28', 's29', 's26', 's27',
            's30', 's32', 's31', 's34', 's33'
        ]
        col_width = fix_plot_size(df, x, hue, scale=2)
        hue_order = sorted(df[hue].unique())
        if SHOW_ERROR_BAR:
            ax = sns.barplot(df, x=x, y=y, hue=hue, hue_order=hue_order, estimator=estimator, width=col_width)
        else:
            ax = sns.barplot(df, x=x, y=y, hue=hue, hue_order=hue_order, estimator=estimator, width=col_width,
                             errorbar=None)
        return ax

    def fix_axis(self, metric: str, ax: Axes):
        if self.include_all:
            custom_error = 0.1
            # bar = ax.patches[6]
            # x = bar.get_x() + bar.get_width() / 2
            # y = bar.get_height()
            # ax.errorbar(x=x, y=y, yerr=custom_error, capsize=1, color='black')

        if self.df[metric].max() - self.df[metric].min() <= 1:
            ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
            ax.set_yticklabels([f'{y:.0%}' for y in ax.get_yticks()])

    def save_fig(self, metric, ax: Axes, sub_dir: Optional[str] = None):
        title = ax.get_title()
        ax.set_title("")
        if sub_dir is None:
            save_dir = os.path.join(self.out_dir, self.hue)
        else:
            save_dir = os.path.join(self.out_dir, sub_dir)
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, f"{snakecase(title)}.png")
        plt.savefig(path, bbox_inches='tight', dpi=300)
        logger.info(f"Plot saved to {path}")
        plt.close()

    def draw_metric_mean(self, x: str, metric: str):
        df = self.df
        if self.include_all:
            df = self.add_overall(df, x)
        num_x = self.df[x].nunique()
        width = max(5, num_x * (bar_width + bar_spacing))
        fig = plt.figure(figsize=(width, 5))
        ax = self.draw_barplot(df, x, metric, self.hue, "mean")
        self.fix_axis(metric, ax)
        title = f"Mean {metric} per {x}"
        ax.set_title(title)
        self.save_fig(metric, ax)
        if self.show:
            fig.show()

    def grid_2d(self, row, col, x, metric: str, save_indiv: bool = True):
        df = self.df
        rows = natsorted(df[row].unique())
        cols = natsorted(df[col].unique())
        fig = plt.figure()
        suptitle = f"Mean {metric} per {x} for each {row} and {col}"
        subdir = os.path.join(self.metric_dir(metric), snakecase(suptitle))
        os.makedirs(subdir, exist_ok=True)
        if not save_indiv:
            gs = fig.add_gridspec(nrows=len(rows), ncols=len(cols), hspace=0.5)
            fig.set_size_inches(30, 20)
            axs = gs.subplots(sharey=True)
        for i, row_val in enumerate(rows):
            for j, col_val in enumerate(cols):
                if not save_indiv:
                    ax = axs[i, j]
                    title = f"{row} = {row_val} and {col} = {col_val}"
                else:
                    title = f"Mean {metric} per {x} for {row} = {row_val} and {col} = {col_val}"
                    ax = fig.gca()
                    ax.cla()
                ax.set_title(title)
                sub_df = df[(df[row] == row_val) & (df[col] == col_val)]
                sub_cats = natsorted(sub_df[x].unique())
                sns.barplot(sub_df, x=x, y=metric, hue=self.hue, estimator="mean", ax=ax, legend=False,
                            order=sub_cats)
                self.fix_axis(metric, ax)
                if save_indiv:
                    fig.savefig(os.path.join(subdir, f'{snakecase(ax.get_title())}.png'), bbox_inches='tight')
        if not save_indiv:
            fig.suptitle(suptitle)
            plt.savefig(os.path.join(self.metric_dir(metric), f"{snakecase(suptitle)}.png"), bbox_inches='tight')
            if self.show:
                plt.show()

    def grid_1d(self, col, x, metric: str, save_indiv: bool = True, row: bool = False):
        df = self.df
        cats = natsorted(df[col].unique())
        suptitle = f"Mean {metric} per {x} for each {col}"
        subdir = os.path.join(self.metric_dir(metric), snakecase(suptitle))
        os.makedirs(subdir, exist_ok=True)
        if not save_indiv:
            if row:
                fig = plt.figure(figsize=(25, height * 2))
                gs = fig.add_gridspec(nrows=len(cats), hspace=1.5)
            else:
                fig = plt.figure(figsize=(25, height * 2))
                widths = self.df.groupby(col)[x].nunique()
                gs = fig.add_gridspec(ncols=len(cats), hspace=1.5, width_ratios=widths)
            axs = gs.subplots(sharey=True)
        for ci, col_val in enumerate(cats):
            if not save_indiv:
                ax = axs[ci]
                title = f"{col} = {col_val}"
            else:
                title = f"Mean {metric} per {x} for {col} = {col_val}"
                fig = plt.figure(figsize=(10, height))
                ax = fig.gca()
                ax.cla()
            ax.set_title(title)
            sub_df = df[(df[col] == col_val)]
            sub_cats = natsorted(sub_df[x].unique())
            sns.barplot(sub_df, x=x, y=metric, hue=self.hue, estimator="mean", ax=ax, legend=False,
                        order=sub_cats)
            self.fix_axis(metric, ax)
            if save_indiv:
                plt.savefig(os.path.join(subdir, f"{snakecase(ax.get_title())}.png"), bbox_inches='tight', dpi=300)
                if self.show:
                    plt.show()
        if not save_indiv:
            fig.suptitle(suptitle)
            plt.savefig(os.path.join(self.metric_dir(metric), f"{snakecase(suptitle)}.png"))
            if self.show:
                plt.show()

    def draw(self, metric: str):
        # os.makedirs(self.metric_dir(metric), exist_ok=True)
        # self.draw_metric_mean("Temp", metric)
        self.draw_metric_mean("Category", metric)
        self.draw_metric_mean("SubCategory", metric)
        # self.grid_1d("Category", "SubCategory", metric)
        # self.grid_1d("Category", "SubCategory", metric, save_indiv=False)
        # self.grid_1d("Category", "Temp", metric)
        # self.grid_1d("Category", "Temp", metric, save_indiv=False)
        # self.grid_1d("Temp", "Category", metric)
        # self.grid_1d("Temp", "Category", metric, save_indiv=False)
        # self.grid_1d("Temp", "SubCategory", metric, row=True)
        # self.grid_1d("Temp", "SubCategory", metric, row=True, save_indiv=False)
        # self.grid_2d("Category", "Temp", "SubCategory", metric)
        # self.grid_2d("Category", "Temp", "SubCategory", metric, save_indiv=False)

    def draw_cats(self):
        df = self.df
        subs = natsorted(df['SubCategory'].unique())
        cats = natsorted(df['Category'].unique())
        vers = natsorted(df['Workload Version'].unique())
        hue = 'Workload Version'
        x = 'Category'
        col_width = fix_plot_size(df, x, hue=hue, scale=3)

        temp = df["Temp"].unique()[0]
        model = df["Model"].unique()[0]
        itr = df["itr"].unique()[0]
        scale = df["scale"].unique()[0]
        df = df[(df['Temp'] == temp) & (df["Model"] == model) & (df['itr'] == itr) & (df['scale'] == scale)]

        ax = sns.countplot(df, x=x, hue=hue, hue_order=vers, order=cats, width=col_width)

        os.makedirs(os.path.join(self.out_dir, hue), exist_ok=True)
        plt.savefig(os.path.join(self.out_dir, hue, f"cat_count.png"))
        plt.clf()

        # plt.figure(figsize=(50, 5))
        sns.countplot(df, x="SubCategory", hue=hue, hue_order=vers, order=subs)
        plt.savefig(os.path.join(self.out_dir, hue, f"sub_cat_count.png"))
        if self.show:
            plt.show()

    def draw_overall(self):
        print("DRAWING OVERALL")
        df = melt_scores(self.df)
        cat_avg = (
            df.groupby(["Model", "Dataset", "Workload Version", "Metric", "Category"], observed=False)["Score"]
            .mean()
            .reset_index()
        )
        macro_avg = (
            cat_avg.groupby(["Model", "Dataset", "Workload Version", "Metric"], observed=False)["Score"]
            .mean()
            .reset_index()
        )

        x = "Metric"
        col_width = fix_plot_size(df, x, hue=self.hue, scale=3)

        plt.title("Overall Scores")
        # ax = sns.barplot(df, x="Metric", y="Score", hue=self.hue)
        hue_order = sorted(macro_avg[self.hue].unique())
        ax = sns.barplot(macro_avg, x="Metric", y="Score", hue=self.hue, hue_order=hue_order, width=col_width)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels([f'{y:.0%}' for y in ax.get_yticks()])
        self.save_fig("overall", ax)
        # plt.savefig(os.path.join(self.out_dir, f"overall.png"))

    def draw_scale_plot(self, metric):
        df = self.df
        if metric not in df.columns:
            return

        x = 'scale'
        # num_x = self.df[x].nunique()
        # width = max(5, num_x * (bar_width + bar_spacing))
        # fig = plt.figure(figsize=(width, 5))
        fix_plot_size(df, x, hue=self.hue, scale=2)
        ax = self.draw_barplot(df, x, metric, self.hue, "mean")
        self.fix_axis(metric, ax)
        title = f"Mean {metric} per {x}"
        ax.set_title(title)
        self.save_fig(metric, ax, "Scale")
        # if self.show:
        #     fig.show()

    def draw_all(self):
        pass
        # for metric in ["ea", "em", "cc", "etc", "et", "tokens"]:
        #     self.draw(metric)
