from abc import abstractmethod, ABC
from typing import List, TypeVar, Generic

from pandas import DataFrame

from src.sql_parser.node import SqlAstNode
from src.util.file_utils import save_csv
from src.util.multi_thread import process_multi_thread

T = TypeVar('T')


class BatchAstExporterProcessor(ABC, Generic[T]):
    """Processes a list of ASTs and export the result as a CSV file"""

    def __init__(self, out_path: str):
        self.out_path = out_path

    def process(self, ast_list: List[SqlAstNode]):
        # ****IMPORTANT NOTE!**** Multi thread processing might change the order of data!
        data = process_multi_thread(self.process_ast, ast_list, self.__class__.__name__)
        df = DataFrame(data)
        save_csv(df, self.out_path)
        return df

    @abstractmethod
    def process_ast(self, ast: SqlAstNode) -> T:
        pass
