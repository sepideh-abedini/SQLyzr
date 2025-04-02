import os.path

import pandas as pd
import seaborn as sns
from dataclasses_json.stringcase import snakecase
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.transforms import Bbox
from natsort import natsorted
from pandas import DataFrame

ET_TRESH = 0.1
TOP_TEMP = 0.2

COL_NAMES = {
    "ea": "Execution Accuracy",
    "rea": "Relaxed Execution Accuracy",
    "em": "Exact Match",
    "sem": "Spider Exact Match",
    "et": "Execution Time",
    "etc": "Execution Time Consistency",
    "cconst": "Complexity Consistency",
    "tokens": "Token Usage",
    "cat": "Category",
    "sub_cat": "SubCategory",
    "model": "Model",
    "dataset": "Dataset",
    "tmp": "Temp"
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


def proc_df(scores_path: str):
    df = pd.read_csv(scores_path)
    df = df.dropna(subset=["cat"])
    cats = natsorted(df['cat'].unique())
    sub_cats = natsorted(df['sub_cat'].unique())
    df['cat'] = pd.Categorical(df['cat'], categories=cats, ordered=True)
    df['sub_cat'] = pd.Categorical(df['sub_cat'], categories=sub_cats, ordered=True)
    df['etc'] = (df['et'] < df['get'] * (1 + ET_TRESH)).astype(int)
    df['etc'] = (df['etc'] & df["ea"])
    df["cconst"] = (df["cc"] & df["ea"])
    df = df.drop(columns=[col for col in df.columns if "Unnamed" in col])

    df = df[df['tmp'] == TOP_TEMP]

    mean_values = df.drop(columns=['cat', 'sub_cat', "dataset"]).groupby('model').mean()
    for value in df['model'].unique():
        new_row = {'model': value, 'cat': "all", "sub_cat": "all"}
        new_row.update(mean_values.loc[value].to_dict())
        row = pd.DataFrame([new_row])
        df = pd.concat([df, row], ignore_index=True)

    df = df.rename(columns=COL_NAMES)

    df.to_csv("charts/data.csv", index=False)
    return df


def melt_scores(df):
    df["Complexity Consistency"] = (df["cc"] & df["ea"])
    df = df.rename(columns=COL_NAMES)
    df = pd.melt(df, id_vars=['Model', 'Dataset', 'Category', 'Temp', 'Sub-Category'],
                 value_vars=['Execution Accuracy', 'Relaxed Execution Accuracy', 'Exact Match',
                             'Complexity Consistency', "Execution Time Consistency"],
                 var_name="Metric",
                 value_name="Score")

    return df


OUT_DIR = "charts"


class Drawer:
    df: DataFrame

    def __init__(self, scores_path: str, show: bool = False):
        self.df = proc_df(scores_path)
        self.show = show

    def metric_dir(self, metric):
        return os.path.join(OUT_DIR, snakecase(metric))

    def draw_barplot(self, x: str, y: str, hue: str, estimator: str):
        ax = sns.barplot(self.df, x=x, y=y, hue=hue, estimator=estimator, width=0.8)
        return ax

    def fix_axis(self, metric: str, ax: Axes):
        if self.df[metric].max() - self.df[metric].min() <= 1:
            ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
            ax.set_yticklabels([f'{y:.0%}' for y in ax.get_yticks()])

    def save_fig(self, metric, ax: Axes):
        title = ax.get_title()
        path = os.path.join(self.metric_dir(metric), f"{snakecase(title)}.png")
        plt.savefig(path, bbox_inches='tight', dpi=300)

    def draw_metric_mean(self, x: str, metric: str):
        num_x = self.df[x].nunique()
        width = max(5, num_x * (bar_width + bar_spacing))
        fig = plt.figure(figsize=(width, 5))
        ax = self.draw_barplot(x, metric, "Model", "mean")
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
                sns.barplot(sub_df, x=x, y=metric, hue="Model", estimator="mean", ax=ax, legend=False,
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
            sns.barplot(sub_df, x=x, y=metric, hue="Model", estimator="mean", ax=ax, legend=False,
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
        os.makedirs(self.metric_dir(metric), exist_ok=True)
        # self.draw_metric_mean("Temp", metric)
        # self.draw_metric_mean("Category", metric)
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

    def draw_all(self):
        pass
        # for metric in ["ea", "em", "cc", "etc", "et", "tokens"]:
        #     self.draw(metric)
