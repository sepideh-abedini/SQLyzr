from typing import Set

from src.parse.node import ColumnNode
from src.parse.visitor.collector_visitor import CollectorVisitor
from src.parse.visitor.visitor_result import MergeableVisitorResult


class ColSet(MergeableVisitorResult):
    cols: Set[str]

    def __init__(self, cols=None):
        if cols is None:
            self.cols = set()
        else:
            self.cols = cols

    def merge(self, other):
        if isinstance(other, ColSet):
            self.cols.update(other.cols)
        return self

    def add(self, value: str):
        self.cols.add(value)

    def __str__(self):
        return str(self.cols)

    def __iter__(self):
        return self.cols.__iter__()

    def __len__(self):
        return len(self.cols)

    def __sub__(self, other):
        return self.cols - other.cols


class ColCollector(CollectorVisitor):
    def __init__(self):
        super().__init__(ColSet)

    def visit_column(self, node: ColumnNode):
        if isinstance(node.column_name.value, str):
            return ColSet({node.column_name.value.lower()})
        else:
            return ColSet()
