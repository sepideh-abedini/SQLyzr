import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from natsort import natsorted  # or use the re.split method from before
from sympy.printing.pretty.pretty_symbology import line_width

from latest.lib import config_plt

config_plt(plt)

def draw_with_histplot():
    # 1. Load and Filter
    df_sqlyzr = pd.read_csv("sqlyzr_c1_s4.csv")
    df_sqlyzr = df_sqlyzr[(df_sqlyzr['tmp'] == 0.2) & (df_sqlyzr['model'] == "din") & (df_sqlyzr['itr'] == 0)]
    df_sqlyzr['Corpus'] = 'SQLyzr'

    df_sqlshare = pd.read_csv("sqlshare_c1_s4.csv")
    df_sqlshare = df_sqlshare[df_sqlshare['cat'] != "c1000"]
    df_sqlshare['Corpus'] = 'SQLShare'

    # 2. Combine
    df_combined = pd.concat([df_sqlyzr, df_sqlshare], ignore_index=True)
    df_combined["Category"] = df_combined['cat']

    # 3. Define natural sort order for the x-axis
    sorted_order = natsorted(df_combined['Category'].unique())

    df_combined['Category'] = pd.Categorical(df_combined['Category'], categories=sorted_order, ordered=True)
    # 4. Plotting
    plt.figure(figsize=(10, 6))

    sns.histplot(
        data=df_combined,
        x="Category",
        hue="Corpus",
        hue_order=["SQLyzr", "SQLShare"],
        multiple="dodge",  # Puts bars side-by-side
        stat="percent",  # Changes y-axis to percentage
        common_norm=False,  # IMPORTANT: Each corpus sums to 100% independently
        shrink=0.8,  # Adds space between category groups
        hue_norm=None,  # Keeps colors consistent,
        alpha=1.0,  # 1.0 is solid, 0.2 is very pale/transparent
        edgecolor="red",  # Adding edges helps pale bars stay visible
        linewidth=0,
    )

    # plt.title("Category Distribution Comparison")
    plt.ylabel("Percentage within Corpus (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(f"dist-comp.png"), bbox_inches='tight', dpi=300)
    plt.show()


draw_with_histplot()
