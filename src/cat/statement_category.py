from typing import Set

from src.cat.tag_set import TagSet


class StatementCategory:
    name: str
    tag_sets: Set[TagSet]

    def __init__(self, name: str, *tag_sets: TagSet):
        self.name = name
        self.tag_sets = set(tag_sets)

    def matches(self, feature_set: TagSet):
        for fs in self.tag_sets:
            if feature_set >= fs:
                return True
        return False
