from typing import List

from src.cat.statement_category import StatementCategory
from src.cat.sub_category import SubCategory
from src.cat.statement_tag import *

CAT_1 = StatementCategory(
    "c1",
    SubCategory("s1", frozenset([SelectType.SingleColumn]))
)

CAT_2 = StatementCategory(
    "c2",
    SubCategory("s2", frozenset([SelectType.MultiColumn])),
    SubCategory("s3", frozenset([ExtraKeywords.OrderBy]))
)

CAT_3 = StatementCategory(
    "c3",
    SubCategory("s4", frozenset([WhereType.SingleWhereExpr, ExprType.SingleBinExpr])),
    SubCategory("s5", frozenset([ExprType.ArithExpr])),
    SubCategory("s6", frozenset([ExtraKeywords.Limit])),
    SubCategory("s7", frozenset([ExtraKeywords.Distinct])),
    SubCategory("s8", frozenset([GroupType.UnconditionalGroup])),
    SubCategory("s9", frozenset([JoinConditions.UnconditionalJoin, JoinTables.SingleJoin])),
)

CAT_4 = StatementCategory(
    "c4",
    SubCategory("s10", frozenset([WhereType.MultipleWhereExpr])),
    SubCategory("s11", frozenset([ExprType.ComplexExpr])),
    SubCategory("s12",
                frozenset([GroupType.UnconditionalGroup, WhereType.SingleWhereExpr])),
    SubCategory("s13", frozenset([JoinConditions.UnconditionalJoin, WhereType.SingleWhereExpr])),
    SubCategory("s14",
                frozenset([GroupType.UnconditionalGroup, JoinConditions.UnconditionalJoin])),
    SubCategory("s15", frozenset([GroupType.ConditionalGroup])),
    SubCategory("s16", frozenset([JoinConditions.ConditionalJoin])),
    SubCategory("s17", frozenset([StructureType.Compound]))
)

CAT_5 = StatementCategory(
    "c5",
    SubCategory("s18", frozenset([StructureType.Nested]))
)

CAT_6 = StatementCategory(
    "c6",
    SubCategory("s19", frozenset([StructureType.Nested, GroupType.UnconditionalGroup])),
    SubCategory("s20", frozenset([StructureType.Nested, JoinConditions.UnconditionalJoin])),
    SubCategory("s21", frozenset([StructureType.Compound, StructureType.Nested])),
)

CATS = [CAT_1, CAT_2, CAT_3, CAT_4, CAT_5, CAT_6]


def get_all_sub_cats(cats: List[StatementCategory]):
    sub_cats = []
    for cat in cats:
        for sub_cat in cat.sub_cats:
            # sub_cat_full_name = f"{cat.name}_{sub_cat.name}"
            sub_cat_full_name = f"{sub_cat.name}"
            sub_cats.append(sub_cat_full_name)
    return sub_cats


def get_all_cats(cats: List[StatementCategory]):
    return list(map(lambda c: c.name, cats))
