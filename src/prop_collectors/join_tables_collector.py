from src.prop_collectors.sql_features import SqlFeatures
from src.sql_parser.node import JoinClauseNode
from src.visitor.collector_visitor import CollectorVisitor


class JoinTablesCollector(CollectorVisitor):
    def __init__(self):
        super().__init__(SqlFeatures)

    def visit_join_clause(self, node: JoinClauseNode):
        return SqlFeatures(join_tables_count_list=[len(node.tables)])
