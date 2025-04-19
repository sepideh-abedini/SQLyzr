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
INCLUDE_ALL = True

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
    "sub": "SubCategory",
    "cdiff": "Complexity Inconsistency",
    "etcdiff": "Execution Time Inconsistency",
    "model": "Model",
    "dst": "Dataset",
    "tmp": "Temp",
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
    df = pd.melt(df, id_vars=['Model', 'Dataset', 'Category', 'Temp', 'SubCategory'],
                 value_vars=['Execution Accuracy', 'Relaxed Execution Accuracy', 'Exact Match',
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

    def __init__(self, scores_path: str, include_all: bool = False, only_correct: bool = False,
                 exclude_c6: bool = False, show: bool = False):
        self.show = show
        self.include_all = include_all
        self.only_correct = only_correct
        self.exclude_c6 = exclude_c6
        self.df = self.proc_df(scores_path)

    def proc_df(self, scores_path: str):
        df = pd.read_csv(scores_path)
        df = df.dropna(subset=["cat"])
        cats = natsorted(df['cat'].unique())
        sub_cats = natsorted(df['sub'].unique())
        df['cat'] = pd.Categorical(df['cat'], categories=cats, ordered=True)
        df['sub'] = pd.Categorical(df['sub'], categories=sub_cats, ordered=True)
        df = df.sort_values(by=['cat', 'sub'])
        if self.only_correct:
            df = df[df['rea'] == 1]
        df['etc'] = (df['et'] < df['get'] * (1 + ET_TRESH)).astype(int)
        df['etc'] = df['plt']
        df["cconst"] =df["plc"]
        df["cdiff"] = ~df["plc"]
        df["etcdiff"] = ~df["plt"]
        df['diff'] = df['rea'] - df['ea']
        df = df.drop(columns=[col for col in df.columns if "Unnamed" in col])
        df = df.drop(columns=['pcat','psub'])
        if self.exclude_c6:
            df = df[df['cat'] != 'c6']

        df = df[df['tmp'] == TOP_TEMP]

        if self.include_all:
            # mean_values = df.drop(columns=['cat', 'sub_cat', "dataset"]).groupby('model').mean()
            # for value in df['model'].unique():
            #     new_row = {'model': value, 'cat': "all", "sub_cat": "all"}
            #     new_row.update(mean_values.loc[value].to_dict())
            #     row = pd.DataFrame([new_row])
            #     df = pd.concat([df, row], ignore_index=True)
            mean_values = df.drop(columns=['sub', "dst"]).groupby(['model', 'cat']).mean()
            mean_values = mean_values.groupby(['model']).mean()
            #
            for value in df['model'].unique():
                new_row = {'model': value, 'cat': "all", "sub": "all"}
                new_row.update(mean_values.loc[value].to_dict())
                row = pd.DataFrame([new_row])
                df = pd.concat([df, row], ignore_index=True)

        df = df.rename(columns=COL_NAMES)

        df.to_csv("charts/data.csv", index=False)
        return df

    def metric_dir(self, metric):
        return os.path.join(OUT_DIR, snakecase(metric))

    def draw_barplot(self, x: str, y: str, hue: str, estimator: str):
        order = [
            's0',
            's1', 's2',
            's8', 's6', 's3', 's9', 's7', 's4', 's5',
            's16', 's17', 's13', 's19', 's12', 's11', 's14', 's15', 's18',
            's20', 's21', 's22', 's25', 's24',
            's28', 's29', 's26', 's27',
            's30', 's32', 's31', 's34', 's33'
        ]
        ax = sns.barplot(self.df, x=x, y=y, hue=hue, estimator=estimator, width=0.8)
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

    def save_fig(self, metric, ax: Axes):
        title = ax.get_title()
        ax.set_title("")
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
        self.draw_metric_mean("Category", metric)
        # self.draw_metric_mean("SubCategory", metric)
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
        df = df[(df['Temp'] == 0.2) & (df['Model'] == "din") & (df['itr'] == 0)]
        plt.figure(figsize=(5, 5))

        sns.countplot(df, x="Category")
        plt.savefig(os.path.join(OUT_DIR, f"cat_count.png"))

        plt.figure(figsize=(50, 5))
        sns.countplot(df, x="SubCategory")
        plt.savefig(os.path.join(OUT_DIR, f"sub_cat_count.png"))

        plt.show()

    def draw_overall(self):
        df = melt_scores(self.df)
        plt.figure(figsize=(15, 5))
        ax = sns.barplot(df, x="Metric", y="Score", hue="Model")
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels([f'{y:.0%}' for y in ax.get_yticks()])
        plt.savefig(os.path.join(OUT_DIR, f"overall.png"))

    def draw_all(self):
        pass
        # for metric in ["ea", "em", "cc", "etc", "et", "tokens"]:
        #     self.draw(metric)
