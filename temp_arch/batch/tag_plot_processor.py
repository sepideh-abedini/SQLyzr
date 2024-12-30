from matplotlib import pyplot as plt
from pandas import DataFrame

from src.batch.csv_file_processor import CsvFileProcessor


class TagPlotProcessor(CsvFileProcessor):

    def get_columns(self):
        return []

    def process_df(self, df: DataFrame) -> DataFrame:
        n_cols = 3
        n_rows = 4
        fig, axs = plt.subplots(n_rows, n_cols, figsize=(10, 10))
        for i, tt in enumerate(df.columns):
            row = int(i / n_cols)
            col = i % n_cols
            counts = df[tt].value_counts(dropna=False)
            sub_plt = axs[row, col]
            sub_plt.set_title(tt)
            sub_plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%', startangle=140)
        plt.show()
        return df
