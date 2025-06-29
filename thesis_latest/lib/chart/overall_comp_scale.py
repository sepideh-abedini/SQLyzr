import argparse

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from thesis.lib import config_plt, pre_process_df


def melt_scores(df):
    df = pd.melt(df, id_vars=['model', 'dst', 'cat', 'tmp', 'sub', 'Dataset'],
                 value_vars=['ea', 'rea', 'em', 'etc', 'cc'],
                 var_name="Metric",
                 value_name="Score")
    df['Metric'] = df['Metric'].replace({'ea': 'EA', 'rea': 'REA', 'etc': 'ETC', 'cc': 'CC', 'em': 'EM'})

    return df


def draw_overall(df, out_file):
    df = melt_scores(df)
    plt.figure(figsize=(12, 12))
    # ax = sns.barplot(df, x="Metric", y="Score", hue="aligned", saturation=1)
    facet = sns.catplot(
        data=df,
        x="Metric",
        y="Score",
        hue="Dataset",
        row="model",
        kind="bar",
        palette="tab10",
        height=5,
        aspect=1.5,
        saturation=1,
    )
    # ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))

    # handles, labels = ax.get_legend_handles_labels()

    # ci_handle = ax.errorbar(
    #     [np.nan], [np.nan],
    #     xerr=[10],
    #     fmt='none',
    #     ecolor='black',
    #     elinewidth=3.5,
    #     capsize=0,
    #     label='95% CI'
    # )
    #
    # handles.append(ci_handle)
    # labels.append('95% CI')
    # ax.legend(handles=handles, labels=labels)

    plt.savefig(out_file)

    wide_df = df.pivot_table(index='model', columns='Metric', values='Score', aggfunc='mean')
    wide_df = wide_df[["EA", "REA", "EM", "ETC", "CC"]]
    wide_df = wide_df.applymap(lambda x: f"{x:.2f}%")
    wide_df.to_csv(out_file.replace('.png', '.csv'))


def main(in_file, align_file, scale_file, out_file):
    aa = pd.read_csv(align_file)
    sd = pd.read_csv(scale_file)
    sd['pcat'] = aa['pcat']
    sd.to_csv(scale_file)
    config_plt(plt)
    aa = pre_process_df(align_file)
    print("HERE")
    print(aa.keys())
    df = pre_process_df(in_file)
    # df['pcat'] = aa['pcat']
    df['Dataset'] = 'Original'
    adf = pre_process_df(scale_file)
    adf['Dataset'] = 'Scaled (x1000)'
    # adf['pcat'] = aa['pcat']

    combined = pd.concat([df, adf], ignore_index=True)

    draw_overall(combined, out_file)
    # plt.title('Overall Score')
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-a", required=True)
    parser.add_argument("-s", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.a, args.s, args.o)
