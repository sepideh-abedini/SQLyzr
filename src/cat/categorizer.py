from typing import List

from src.cat.categories import CAT_1, CAT_2, CAT_3, CAT_4, CAT_5, CAT_6
from src.cat.statement_category import StatementCategory
from src.cat.tag_set import TagSet


class Categorizer:
    categories: List[StatementCategory]

    def __init__(self, categories=None):
        if categories is None:
            categories = [CAT_1, CAT_2, CAT_3, CAT_4, CAT_5, CAT_6]
        self.categories = categories

    def get_category(self, tag_set: TagSet):
        for c in reversed(
                self.categories):  # Check to find a match starting from
            # harder categories
            if c.matches(tag_set):
                return c.name
        return None
