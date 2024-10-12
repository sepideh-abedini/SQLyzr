from src.cat.statement_category import StatementCategory
from src.cat.tag_set import TagSet
from src.cat.statement_tag import *

CAT_1 = StatementCategory(
    "c1",
    TagSet(frozenset([SelectType.SingleColumn]))
)

CAT_2 = StatementCategory(
    "c2",
    TagSet(frozenset([SelectType.MultiColumn])),
    TagSet(frozenset([ExtraKeywords.OrderBy]))
)

CAT_3 = StatementCategory(
    "c3",
    TagSet(frozenset([WhereType.SingleWhereExpr, ExprType.SingleBinExpr])),
    TagSet(frozenset([ExprType.ArithExpr])),
    TagSet(frozenset([ExtraKeywords.Limit])),
    TagSet(frozenset([ExtraKeywords.Distinct])),
    TagSet(frozenset([GroupType.UnconditionalGroup])),
    TagSet(frozenset([JoinConditions.UnconditionalJoin, JoinTables.SingleJoin])),
)

CAT_4 = StatementCategory(
    "c4",
    TagSet(frozenset([WhereType.MultipleWhereExpr])),
    TagSet(frozenset([ExprType.ComplexExpr])),
    TagSet(
        frozenset([GroupType.UnconditionalGroup, WhereType.SingleWhereExpr])),
    TagSet(frozenset([JoinConditions.UnconditionalJoin, WhereType.SingleWhereExpr])),
    TagSet(
        frozenset([GroupType.UnconditionalGroup, JoinConditions.UnconditionalJoin])),
    TagSet(frozenset([GroupType.ConditionalGroup])),
    TagSet(frozenset([JoinConditions.ConditionalJoin])),
    TagSet(frozenset([StructureType.Compound]))
)

CAT_5 = StatementCategory(
    "c5",
    TagSet(frozenset([StructureType.Nested]))
)

CAT_6 = StatementCategory(
    "c6",
    TagSet(frozenset([StructureType.Nested, GroupType.UnconditionalGroup])),
    TagSet(frozenset([StructureType.Nested, JoinConditions.UnconditionalJoin])),
    TagSet(frozenset([StructureType.Compound, StructureType.Nested])),
)
