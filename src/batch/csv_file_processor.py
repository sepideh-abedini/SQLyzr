from abc import ABC, abstractmethod
from typing import List

from pandas import DataFrame

from src.util.file_utils import load_csv, save_csv


class CsvFileProcessor(ABC):
    """Reads a CSV file as dataframe, do a processing and returns a resulting dataframe"""
    in_path: str

    def __init__(self, in_path: str):
        self.in_path = in_path

    def process(self):
        in_df = load_csv(self.in_path)
        assert self.df_has_columns(in_df)
        out_df = self.process_df(in_df)
        return out_df

    def df_has_columns(self, df: DataFrame) -> bool:
        for col in self.get_columns():
            if col not in df.columns.values:
                print(f"Missing column {col} in {self.in_path}")
                return False
        return True

    @abstractmethod
    def get_columns(self) -> List[str]:
        pass

    @abstractmethod
    def process_df(self, df: DataFrame) -> DataFrame:
        pass
