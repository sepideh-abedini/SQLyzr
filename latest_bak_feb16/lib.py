import pandas as pd
from natsort import natsorted

ETC_RATIO = 1.1


def pre_process_df(path, micro: bool = False):
    print("HERE")
    df = pd.read_csv(path)
    print("KEYS:")
    print(df.keys())
    df["model"] = df["model"].str.upper()
    df["cat"] = df["cat"].str.upper()
    df["sub"] = df["sub"].str.upper()
    df = df.dropna(subset=["cat"])
    cats = natsorted(df['cat'].unique())
    sub_cats = natsorted(df['sub'].unique())
    df['cat'] = pd.Categorical(df['cat'], categories=cats, ordered=True)
    df['sub'] = pd.Categorical(df['sub'], categories=sub_cats, ordered=True)
    df = df.drop(columns=[col for col in df.columns if "Unnamed" in col])
    df = df.drop(columns=['pcat', 'psub', 'id'], errors='ignore')
    df["cdiff"] = 1 - df["plc"]
    df["etcdiff"] = 1 - df["plt"]
    df['etc'] = df.apply(lambda e: int((e['et'] / e['get']) <= ETC_RATIO), axis=1)
    # df['etc'] = 1 - df['etc']
    # df['plc'] = 1 - df['plc']
    metrics = ['etc','plt', 'plc', 'cdiff', 'etcdiff', 'ea', 'rea', 'em']
    df[metrics] = df[metrics] * 100
    dfe = df[['model', 'cat', 'plc']]
    dfe.to_csv('dfe.csv')

    if micro:
        micro_values = (
            df.drop(columns=["cat", "sub", "dst"])
            .groupby("model", observed=False)
            .mean()
        )

        for value in df["model"].unique():
            new_row = {"model": value, "cat": "Overall", "sub": "Overall"}
            new_row.update(micro_values.loc[value].to_dict())
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        mean_values = df.drop(columns=['sub', "dst", "ds_idx"]).groupby(['model', 'cat'], observed=False).mean()
        mean_values = mean_values.groupby(['model']).mean()
        #
        for value in df['model'].unique():
            new_row = {'model': value, 'cat': "Overall", "sub": "Overall"}
            new_row.update(mean_values.loc[value].to_dict())
            row = pd.DataFrame([new_row])
            df = pd.concat([df, row], ignore_index=True)
    return df


def config_plt(plt):
    # Global style settings
    plt.rcParams["font.size"] = 24
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["lines.linewidth"] = 3
    plt.rcParams["legend.fontsize"] = 24
    plt.rcParams['legend.title_fontsize'] = 16
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
