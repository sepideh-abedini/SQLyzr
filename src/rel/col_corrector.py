from typing import Set, Dict

from src.parse.node import ColumnNode
from src.parse.visitor.collector_visitor import CollectorVisitor
from src.parse.visitor.visitor_result import MergeableVisitorResult
from src.util.database_schema import DatabaseSchema, str_similarity


class ColCorrections(MergeableVisitorResult):
    cors: Dict[str, str]

    def __init__(self, cors=None):
        if cors is None:
            self.cors = {}
        else:
            self.cors = cors

    def merge(self, other):
        if isinstance(other, ColCorrections):
            self.cors.update(other.cors)
        return self

    def items(self):
        return self.cors.items()

    def __str__(self):
        return str(self.cors)


class ColCorrector(CollectorVisitor):
    cand_cols: Set[str]

    def __init__(self, db_schema: DatabaseSchema, cand_cols: Set[str]):
        super().__init__(ColCorrections)
        self.cand_cols = cand_cols
        self.db_schema = db_schema

    def visit_column(self, node: ColumnNode):
        if node.table_name:
            best_col = self.db_schema.find_most_similar_column(node.table_name.value, node.column_name.value,
                                                               self.cand_cols)
        else:
            best_col = None
        if best_col and str_similarity(best_col, node.column_name.value) < 1:
            return ColCorrections({node.column_name.value: best_col})
        else:
            return ColCorrections()
