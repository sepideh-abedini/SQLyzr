import tqdm
import seaborn as sns
from matplotlib import pyplot as plt

from scripts.chart_lib.drawer import Drawer, COL_NAMES, proc_df
from src.util.multi_thread_utils import exec_multi_process

SCORES_PATH = "data/all.csv"

# drawer = Drawer(SCORES_PATH)
# metrics = [
# "Execution Accuracy",
# "Relaxed Execution Accuracy",
# "Exact Match",
# "Execution Time",
# "Execution Time Consistency",
# "Token Usage",
# ]

# for metric in tqdm.tqdm(metrics):
#     drawer.draw(metric)

df = proc_df(SCORES_PATH)
plt.figure(figsize=(30, 5))
for i in range(0, 35):
    if f"s{i}" not in df['SubCategory'].unique():
        print(f"s{i} not in df['SubCategory'].unique()")

# ax = sns.countplot(df, x="SubCategory", order=[f"s{i}" for i in range(0, 35)], hue="Model")
# plt.show()
