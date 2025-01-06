from src.cat.tag_collector import TagCollector
from src.cat.tag_collector_result import TagCollectorResult
from src.cat.tags.sql_tag import OrderedTag
from src.parse.node import SelectClauseNode


class SelectColumns(OrderedTag):
    SingleColumn = 1
    MultiColumn = 2

    @staticmethod
    class Collector(TagCollector):

        def visit_select_clause(self, node: SelectClauseNode):
            if len(node.result_columns) == 1:
                return TagCollectorResult(SelectColumns.SingleColumn)
            else:
                return TagCollectorResult(SelectColumns.MultiColumn)
