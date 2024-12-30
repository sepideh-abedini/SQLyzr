from src.sql_parser.node import OrderByNode, GroupClauseNode, LimitNode, \
    BetweenExpressionNode, SelectClauseNode
from src.prop_collectors.sql_features import SqlFeatures
from src.visitor.collector_visitor import CollectorVisitor


class KeywordCollector(CollectorVisitor):
    def __init__(self):
        super().__init__(SqlFeatures)

    def visit_select_clause(self, node: SelectClauseNode):
        features = super().visit_select_clause(node)
        if node.distinct:
            return features + SqlFeatures(has_order_by=True)
        return features

    def visit_order_by(self, node: OrderByNode):
        return SqlFeatures(has_order_by=True)

    def visit_group_clause(self, node: GroupClauseNode):
        return SqlFeatures(has_group=True)

    def visit_limit(self, node: LimitNode):
        return SqlFeatures(has_limit=True)

    def visit_between_expression(self, node: BetweenExpressionNode):
        return SqlFeatures(has_between=True)
