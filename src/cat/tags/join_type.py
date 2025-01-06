from enum import auto

from src.cat.tag_collector import TagCollector
from src.cat.tag_collector_result import TagCollectorResult
from src.cat.tags.sql_tag import SqlTag
from src.parse.node import JoinClauseNode, JoinConstraintNode, BinOpExpressionNode


class JoinType(SqlTag):
    NaturalJoin = 0
    EquiJoin = 1
    NonEquiJoin = 2
    NonSimpleJoin = 3

    @staticmethod
    class Collector(TagCollector):

        def visit_join_clause(self, node: JoinClauseNode):
            tags = super().visit_join_clause(node)
            if all(constr is None for constr in node.constraints):
                tags += TagCollectorResult(JoinType.NaturalJoin)
            if any(op.value.lower() != "join" for op in node.ops):
                tags += TagCollectorResult(JoinType.NonSimpleJoin)
            return tags

        def visit_join_constraint(self, node: JoinConstraintNode):
            if isinstance(node.expr, BinOpExpressionNode):
                if node.expr.op.value == "=":
                    return TagCollectorResult(JoinType.EquiJoin)
            return TagCollectorResult(JoinType.NonEquiJoin)
