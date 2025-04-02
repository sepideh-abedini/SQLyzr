import pandas as pd
from dataclasses_json.stringcase import snakecase
from matplotlib import pyplot as plt
import seaborn as sns

df = pd.read_csv("data/util_stats.csv",index_col=0)
df = df.reset_index(drop=True)

for col in df.columns.tolist():
    print(col)
    if pd.api.types.is_numeric_dtype(df[col]):
        sns.barplot(df, x="Model", y=col, hue="Model", width=0.4)
        plt.tight_layout()
        plt.savefig(f"charts/util/{snakecase(col)}.png")
        plt.show()
