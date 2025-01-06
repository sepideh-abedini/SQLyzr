from enum import auto

from src.cat.tag_collector import TagCollector
from src.cat.tag_collector_result import TagCollectorResult
from src.cat.tags.sql_tag import SqlTag
from src.parse.node import SelectStatementNode


class StructureType(SqlTag):
    Compound = auto()
    Nested = auto()

    @staticmethod
    class Collector(TagCollector):
        cur_level: int

        def __init__(self):
            super().__init__()
            self.cur_level = 0

        def visit_select_statement(self, node: SelectStatementNode):
            self.cur_level += 1
            tags = super().visit_select_statement(node)
            if len(node.set_ops) > 0:
                tags += TagCollectorResult(StructureType.Compound)
            if self.cur_level > 1:
                tags += TagCollectorResult(StructureType.Nested)
            self.cur_level -= 1
            return tags
