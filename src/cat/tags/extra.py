from enum import auto

from src.cat.tag_collector import TagCollector
from src.cat.tag_collector_result import TagCollectorResult
from src.cat.tags.sql_tag import SqlTag
from src.parse.node import LimitNode, OrderByNode, SelectClauseNode


class ExtraKeywords(SqlTag):
    Distinct = auto()
    Limit = auto()
    OrderBy = auto()
    ALL = auto()
    LIKE = auto()
    BETWEEN = auto()
    IS_NULL = auto()
    IN = auto()
    EXISTS = auto()
    AGGREGATE = auto()
    CTE = auto
    PARTITION_BY = auto()
    RANK = auto()

    class ExtraKeywordsTagCollector(TagCollector):
        def visit_select_clause(self, node: SelectClauseNode):
            tags = super().visit_select_clause(node)
            if node.distinct:
                return tags + TagCollectorResult(ExtraKeywords.Distinct)
            return tags

        def visit_limit(self, node: LimitNode):
            return TagCollectorResult(ExtraKeywords.Limit)

        def visit_order_by(self, node: OrderByNode):
            tags = super().visit_order_by(node)
            return tags + TagCollectorResult(ExtraKeywords.OrderBy)
