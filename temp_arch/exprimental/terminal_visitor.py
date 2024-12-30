from typing import Set

from src.parse.node import LiteralNode
from src.parse.visitor.collector_visitor import CollectorVisitor
from src.parse.visitor.visitor_result import MergeableVisitorResult


class ValueSet(MergeableVisitorResult):
    values: Set[str]

    def __init__(self, values=None):
        if values is None:
            self.values = set()
        else:
            self.values = values

    def merge(self, other):
        if isinstance(other, ValueSet):
            self.values.update(other.values)
        return self

    def add(self, value: str):
        self.values.add(value)

    def __str__(self):
        return str(self.values)

    def __iter__(self):
        return self.values.__iter__()

    def __len__(self):
        return len(self.values)


class ValueCollector(CollectorVisitor):
    def __init__(self):
        super().__init__(ValueSet)

    def visit_literal(self, node: LiteralNode):
        if isinstance(node.value, str):
            return ValueSet({node.value})
        else:
            return ValueSet()
