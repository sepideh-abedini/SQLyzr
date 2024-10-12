from src.cat.tag_set import TagSet
from src.cat.statement_tag import *
from src.visitor.visitor_result import MergeableVisitorResult


class TagCollectorResult(MergeableVisitorResult):
    tag_set: TagSet

    def __init__(self, *tags: StatementTag):
        self.tag_set = TagSet(frozenset([*tags]))

    def merge(self, other):
        if isinstance(other, TagCollectorResult):
            self.tag_set += other.tag_set
        return self

    def add(self, tag: StatementTag):
        self.tag_set += tag

    def __str__(self):
        return str(self.tag_set)
