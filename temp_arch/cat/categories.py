from typing import List

from src.cat.statement_category import StatementCategory
from src.cat.sub_category import SubCategory
from src.cat.statement_tag import *

CAT_1 = StatementCategory(
    "c1",
    SubCategory("s1", frozenset([SelectType.SingleColumn]), "Having single column in SELECT clause")
)

CAT_2 = StatementCategory(
    "c2",
    SubCategory("s2", frozenset([SelectType.MultiColumn]), "Having multiple columns in SELECT clause"),
    SubCategory("s3", frozenset([ExtraKeywords.OrderBy]), "Having ORDER_BY keyword")
)

CAT_3 = StatementCategory(
    "c3",
    SubCategory("s4", frozenset([WhereType.SingleWhereExpr, ExprType.SingleBinExpr]),
                "Having single binary expression in the WHERE clause"),
    SubCategory("s5", frozenset([ExprType.ArithExpr]), "Only having arithmetic expressions"),
    SubCategory("s6", frozenset([ExtraKeywords.Limit]), "Having LIMIT keyword"),
    SubCategory("s7", frozenset([ExtraKeywords.Distinct]), "Having Distinct Keyword"),
    SubCategory("s8", frozenset([GroupType.UnconditionalGroup]), "Having GROUP BY clause without HAVING clause"),
    SubCategory("s9", frozenset([JoinConditions.UnconditionalJoin, JoinTables.SingleJoin]),
                "Having JOIN clause over at most two tables without join condition"),
)

CAT_4 = StatementCategory(
    "c4",
    SubCategory("s10", frozenset([WhereType.MultipleWhereExpr]), "Having multiple expressions in WHERE clause"),
    SubCategory("s11", frozenset([ExprType.ComplexExpr]), "Having complex expression in WHERE clause"),
    SubCategory("s12",
                frozenset([GroupType.UnconditionalGroup, WhereType.SingleWhereExpr]),
                "Having GROUP BY clause without HAVING clause plus having single expression in WHERE clause"),
    SubCategory("s13", frozenset([JoinConditions.UnconditionalJoin, WhereType.SingleWhereExpr]),
                "Having a JOIN clause without join condition plus having single expression in WHERE clause"),
    SubCategory("s14",
                frozenset([GroupType.UnconditionalGroup, JoinConditions.UnconditionalJoin]),
                "Having GROUP BY clause without condition plus having JOIN clause without join condition"),
    SubCategory("s15", frozenset([GroupType.ConditionalGroup]), "Having GROUP BY clause without condition"),
    SubCategory("s16", frozenset([JoinConditions.ConditionalJoin]), "Having JOIN clause with join condition"),
    SubCategory("s17", frozenset([StructureType.Compound]), "Having a composition keyword such as INTERSECT or UNION")
)

CAT_5 = StatementCategory(
    "c5",
    SubCategory("s18", frozenset([StructureType.Nested]), "Having nested sub-queries")
)

CAT_6 = StatementCategory(
    "c6",
    SubCategory("s19", frozenset([StructureType.Nested, GroupType.UnconditionalGroup]),
                "Having nested sub-queries plus having GROUP BY clause without condition"),
    SubCategory("s20", frozenset([StructureType.Nested, JoinConditions.UnconditionalJoin]),
                "Having nested sub-queries plus having JOIN clause without join condition"),
    SubCategory("s21", frozenset([StructureType.Compound, StructureType.Nested]),
                "Having a composition keyword such as (INTERSECT or UNION) and having nested sub-queries"),
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
