from src.cat.statement_tag import *
from src.cat.tag_collector_result import TagCollectorResult
from src.parse.node import *
from src.parse.visitor.collector_visitor import CollectorVisitor


class TagCollector(CollectorVisitor):
    def __init__(self):
        super().__init__(TagCollectorResult)


class SelectTagCollector(TagCollector):
    def visit_select_clause(self, node: SelectClauseNode):
        if len(node.result_columns) == 1:
            return TagCollectorResult(SelectType.SingleColumn)
        else:
            return TagCollectorResult(SelectType.MultiColumn)


class TableCountCollector(TagCollector):
    def __init__(self):
        super().__init__()
        self.uniq_table_names = set()

    def visit_from_clause(self, node: FromClauseNode):
        for table in node.tables:
            if table.table_name:
                self.uniq_table_names.add(table.table_name)
