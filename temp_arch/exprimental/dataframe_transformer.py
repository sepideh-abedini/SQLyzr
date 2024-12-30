from abc import ABC

from src.batch.csv_file_processor import CsvFileProcessor
from src.util.file_utils import save_csv


class DataFrameTransformer(CsvFileProcessor, ABC):
    """Reads a CSV file as dataframe, transform it into another dataframe and export it as a CSV file"""
    out_path: str

    def __init__(self, in_path: str, out_path: str):
        super().__init__(in_path)
        self.out_path = out_path

    def process(self):
        out_df = super().process()
        save_csv(out_df, self.out_path)
        return out_df
