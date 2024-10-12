from src.prop_collectors.sql_features import SqlFeatures
from src.sql_parser.node import TableOrSubqueryNode
from src.visitor.collector_visitor import CollectorVisitor


class TablesCollector(CollectorVisitor):
    def __init__(self):
        super().__init__(SqlFeatures)

    def visit_table_or_subquery(self, node: TableOrSubqueryNode):
        if node.table_name:
            return SqlFeatures(table_set={node.table_name.value})
        else:
            return SqlFeatures()
