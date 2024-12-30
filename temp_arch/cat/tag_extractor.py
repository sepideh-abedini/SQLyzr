from src.cat.tag_collector_result import TagCollectorResult
from src.cat.tag_collector import *
from src.sql_parser.node import SqlAstNode


class TagExtractor:
    def extract_tags(self, ast: SqlAstNode) -> TagCollectorResult:
        collectors = [
            SelectTagCollector(),
            WhereTagCollector(),
            ExprTagCollector(),
            GroupTagCollector(),
            JoinTagCollector(),
            JoinTablesTagCollector(),
            ExtraKeywordsTagCollector(),
            StructureTagCollector()
        ]

        tags = TagCollectorResult()
        for collector in collectors:
            tags += ast.accept(collector)

        return tags
