from src.sql_parser.node import SelectStatementNode
from src.visitor.collector_visitor import CollectorVisitor
from src.visitor.node_visitor import NodeVisitor




class ColumnEncoder(CollectorVisitor):
    def visit_select_statement(self, node: SelectStatementNode):
        return [1]
