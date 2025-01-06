from src.cat.tag_collector import *
from src.cat.tags.expr_type import ExprType
from src.cat.tags.group_cond import GroupType
from src.cat.tags.join_cond import JoinConditions
from src.cat.tags.join_num import NumJoins
from src.cat.tags.join_tables import JoinTables
from src.cat.tags.join_type import JoinType
from src.cat.tags.nest_level import NestLevel
from src.cat.tags.select_columns import SelectColumns
from src.cat.tags.structure import StructureType
from src.cat.tags.where_exprs import WhereType
from src.parse.node import SqlAstNode


class TagExtractor:
    def extract_tags(self, ast: SqlAstNode) -> TagCollectorResult:
        collectors = [
            SelectColumns.Collector(),
            ExprType.Collector(),
            GroupType.Collector(),
            JoinConditions.Collector(),
            JoinTables.Collector(),
            # JoinType(),
            # NestLevel(),
            StructureType.Collector(),
            WhereType.Collector()
        ]

        tags = TagCollectorResult()
        for collector in collectors:
            tags += ast.accept(collector)

        return tags
