from src.prop_collectors.sql_features import SqlFeatures
from src.sql_parser.node import SelectStatementNode
from src.visitor.collector_visitor import CollectorVisitor


class NestLevelCollector(CollectorVisitor):
    max_nest: int
    cur_level: int

    def __init__(self):
        super().__init__(SqlFeatures)
        self.max_nest = 0
        self.cur_level = 0

    def visit_select_statement(self, node: SelectStatementNode):
        self.cur_level += 1
        self.max_nest = max(self.cur_level, self.max_nest)
        super().visit_select_statement(node)
        self.cur_level -= 1
        return SqlFeatures(max_nest_level=self.max_nest)
