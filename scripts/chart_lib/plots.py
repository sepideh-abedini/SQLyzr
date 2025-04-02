from matplotlib import pyplot as plt
from natsort import natsorted
from pandas import DataFrame
import seaborn as sns


def grid_cat_tmp_x_sub_cat_y_metric_hue_model(df: DataFrame, metric: str):
    df = df.dropna(subset=["cat"])
    cats = natsorted(df['cat'].unique())
    tmps = natsorted(df['tmp'].unique())
    fig = plt.figure()
    gs = fig.add_gridspec(nrows=len(cats), ncols=len(tmps), hspace=0.5)
    axs = gs.subplots(sharey=True)
    fig.set_size_inches(20, 30)
    for ci, cat in enumerate(cats):
        for ti, tmp in enumerate(tmps):
            ax = axs[ci, ti]
            sub_df = df[(df['cat'] == cat) & (df['tmp'] == tmp)]
            sub_cats = natsorted(sub_df['sub_cat'].unique())
            sns.barplot(sub_df, x="sub_cat", y=metric, hue="model", estimator="mean", ax=ax, legend=False,
                        order=sub_cats)
            ax.set_title(f"Cat = {cat}")
            plt.savefig(f"data/plots/{cat}_{tmp}_{metric}.png")
    plt.show()


def draw_metric_per_cat(df: DataFrame, metric: str):
    sns.barplot(df, x="cat", y=metric, hue="model", estimator="mean")
    plt.show()

def draw_metric_per_sub_cat(df: DataFrame, metric: str):
    sns.barplot(df, x="sub_cat", y=metric, hue="model", estimator="mean")
    plt.show()

def x_metrics_hue_model():
    df = pd.read_csv(SCORES_PATH)
    df = melt_scores(df)
    plt.figure(figsize=(10, 5))
    fig = sns.barplot(df, x="Metric", y="Score", estimator=lambda x: 100 * np.mean(x), hue="Model", palette="rocket")
    plt.gca().set_yticklabels([f"{int(tick)}%" for tick in plt.gca().get_yticks()])
    plt.savefig(f"data/plots/all_cats_scores.png")
    plt.show()


def x_cat_y_score_grid_rows_metric():
    df = pd.read_csv(SCORES_PATH)
    df = melt_scores(df)
    grid = sns.FacetGrid(df, col="Metric")
    grid.map_dataframe(sns.barplot, x='Category', y='Score', hue="Model", order=CATS)
    grid.add_legend(title="Model")
    plt.savefig(f"data/plots/per_cat_scores.png")
    plt.show()


def x_cat_y_score_grid_rows_metric_line():
    df = pd.read_csv(SCORES_PATH)
    df = melt_scores(df)
    df['Category'] = pd.Categorical(df['Category'],
                                    categories=CATS,
                                    ordered=True)
    grid = sns.FacetGrid(df, col="Metric")
    grid.map_dataframe(sns.lineplot, x='Category', y='Score', marker="o", hue="Model")
    grid.add_legend(title="Model")
    plt.savefig(f"data/plots/per_cat_scores_line_plot.png")
    plt.show()


def x_sub_cat_y_score_grid_cat():
    df = pd.read_csv(SCORES_PATH)
    df = melt_scores(df)
    for cat in CATS:
        cdf = df[df['Category'] == cat]
        grid = sns.FacetGrid(cdf, col="Metric", height=4)
        grid.map_dataframe(sns.barplot, x='Sub-Category', y='Score', hue="Model")
        grid.savefig(f"{cat}.png")
        # g.fig.suptitle("Title of the plot", size=16)
        grid.figure.subplots_adjust(top=.9)
        grid.figure.suptitle(f"Category: {cat}", size=15)
        grid.add_legend(title="Model")
        plt.savefig(f"data/plots/{cat}_per_subcat_scores.png")
        plt.show()


def pies():
    data = pd.read_csv("charts/data/cats.csv")
    unique_values = data['dataset'].unique()
    data['perc'] = data.groupby(['dataset'])['count'].transform(lambda x: x / x.sum() * 100)
    data = data.groupby(['dataset', 'cat']).sum().reset_index()

    num_charts = len(unique_values)
    fig, axs = plt.subplots(1, num_charts, figsize=(15, 15))

    for ax, value in zip(axs, unique_values):
        filtered_data = data[data['dataset'] == value]
        sizes = filtered_data['perc']  # Sum values of y and z for the pie chart
        labels = filtered_data['cat']
        colors = {
            'c1': '#FFE6CC',
            'c2': '#FFCC99',
            'c3': '#FFB266',
            'c4': '#FFA500',
            'c5': '#FF8C00',
            'c6': '#FF4500'
        }
        filtered_colors = [color for cat, color in colors.items() if cat in set(labels)]
        explode = [i * 0.1 if sizes.iloc[i] < 1 else 0 for i in range(len(labels))]
        ax.pie(sizes, labels=labels, explode=explode, autopct='%1.2f%%', colors=filtered_colors)
        ax.set_title(f'{value}')

    plt.tight_layout()
    plt.savefig(f"data/plots/cat_dist_per_dataset_pie.png")
    plt.show()


def cat_dist():
    data = pd.read_csv("data/cats.csv")
    data['perc'] = data.groupby(['dataset'])['count'].transform(lambda x: x / x.sum() * 100)
    data = data.groupby(['dataset', 'cat']).sum()
    sns.barplot(data, x='cat', y="perc", hue="dataset", order=['c1', 'c2', 'c3', 'c4', 'c5', 'c6'])
    plt.xlabel("Category")
    plt.ylabel("Percentage")
    plt.ylim(0, 100)
    plt.savefig(f"data/plots/cat_dist_per_dataset_bar.png")
    plt.show()

