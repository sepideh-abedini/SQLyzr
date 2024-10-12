from src.sql_parser.node import SelectStatementNode, ResultColumnNode
from src.prop_collectors.sql_features import SqlFeatures
from src.sql_parser.node import TerminalNode
from src.visitor.collector_visitor import CollectorVisitor


class TerminalCollector(CollectorVisitor):
    def __init__(self):
        super().__init__(SqlFeatures)

    def visit_select_statement(self, node: SelectStatementNode):
        return SqlFeatures(
        )
    def visit_result_column(self, node: ResultColumnNode):
        print("here")
        return SqlFeatures()

    def visit_terminal(self, node: TerminalNode):
        print("here")
        if node.name == 'set_op':
            return SqlFeatures(set_op_set={node.value})
        if node.name == 'bin_op':
            return SqlFeatures(bin_op_set={node.value})
        if node.name == 'fun_name':
            return SqlFeatures(fun_set={node.value})
        return SqlFeatures()
