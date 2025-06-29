import pandas as pd
from natsort import natsorted

from thesis_latest.lib.params import R_VALUE


def cat_rank(cat: str):
    if not isinstance(cat, str):
        return 10000
    assert cat[0].lower() == "c", "invalid: {}".format(cat)
    return int(cat[1:])


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
    df["cdiff"] = 1 - df["plc"]
    df["etcdiff"] = 1 - df["plt"]
    df['et_le_g'] = df.apply(lambda e: int((e['et'] / e['get']) <= R_VALUE), axis=1)
    df['etc'] = df['rea'] * df['et_le_g']
    df['cat_le_g'] = df.apply(lambda e: int(cat_rank(e['pcat']) <= cat_rank(e['cat'])), axis=1)
    df['cc'] = df['rea'] * df['cat_le_g']
    df = df.drop(columns=['pcat', 'psub', 'id'], errors='ignore')
    # df['etc'] = 1 - df['etc']
    # df['plc'] = 1 - df['plc']
    metrics = ['etc', 'cc', 'ea', 'rea', 'em']
    df[metrics] = df[metrics] * 100

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
