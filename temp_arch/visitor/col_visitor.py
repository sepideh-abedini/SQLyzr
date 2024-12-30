from typing import Set

from src.sql_parser.node import *
from src.visitor.collector_visitor import CollectorVisitor
from src.visitor.visitor_result import MergeableVisitorResult


class Cols(MergeableVisitorResult):
    def __init__(self):
        self.cols = set()

    def merge(self, other):
        if isinstance(other, Cols):
            self.cols = self.cols.union(other.cols)
        return self


class ColVisitor(CollectorVisitor):
    def __init__(self):
        super().__init__(Cols)

    def visit_select_clause(self, node: SelectClauseNode):
        cols = set()
        for c in node.result_columns:
            e = c.expr
            if isinstance(e, ColumnNode):
                cols.add(e.column_name.value)
                if node.distinct:
                    cols.add('distinct')
            if isinstance(e, FunctionExpressionNode):
                cols.add((e.fun_name.value, e.expr.column_name.value))
                if node.distinct:
                    cols.add('distinct')

        c = Cols()
        c.cols = cols
        return c

