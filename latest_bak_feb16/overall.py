import numpy as np
import pandas as pd
import matplotlib.ticker as mtick
from matplotlib import pyplot as plt

from latest.lib import pre_process_df, config_plt
import seaborn as sns
import os

from latest.params import LATEST_SCORES_PATH, OUT_DIR


def melt_scores(df):
    df = pd.melt(df, id_vars=['model', 'dst', 'cat', 'tmp', 'sub'],
                 value_vars=['ea', 'rea', 'em', 'plt', 'plc'],
                 var_name="Metric",
                 value_name="Score")
    df['Metric'] = df['Metric'].replace({'ea': 'EA', 'rea': 'REA', 'plt': 'ETC', 'plc': 'CC', 'em': 'EM'})

    return df


def draw_overall(df):
    df = melt_scores(df)
    plt.figure(figsize=(12, 9))
    ax = sns.barplot(df, x="Metric", y="Score", hue="model", saturation=1)
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))

    handles, labels = ax.get_legend_handles_labels()

    ci_handle = ax.errorbar(
        [np.nan], [np.nan],
        xerr=[10],
        fmt='none',
        ecolor='black',
        elinewidth=3.5,
        capsize=0,
        label='95% CI'
    )

    handles.append(ci_handle)
    labels.append('95% CI')
    ax.legend(handles=handles, labels=labels)

    ax.set_ylim(0, 100)
    plt.savefig(os.path.join(OUT_DIR, f"overall.png"))


config_plt(plt)
df = pre_process_df(LATEST_SCORES_PATH)
print(df[['model', 'plt']].groupby(['model']).mean())
print(df.keys())
draw_overall(df)
df = df[["model", "ea", "rea", "em", "plc", "plt"]]
print(df.keys())
print(df.groupby(["model"]).mean())
plt.title('Overall Score')
plt.show()
