from typing import Set

from src.cat.sub_category import SubCategory


class StatementCategory:
    name: str
    sub_cats: Set[SubCategory]

    def __init__(self, name: str, *tag_sets: SubCategory):
        self.name = name
        self.sub_cats = set(tag_sets)

    def __str__(self):
        return self.name

    def matches(self, feature_set: SubCategory):
        matchs = []
        for fs in self.sub_cats:
            if feature_set >= fs:
                matchs.append(fs)
        if len(matchs) > 0:
            return matchs
        return None
