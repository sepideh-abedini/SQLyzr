from abc import ABC, ABCMeta
from enum import Enum, unique, EnumMeta, auto


class StatementTag(Enum):
    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __str__(self):
        return self.name


class OrderedTag(StatementTag):
    def __ge__(self, other):
        """t1 >= t2 ==> t1 is at least as hard as t2"""
        if not isinstance(other, self.__class__):
            return False
        return self.value >= other.value


class SelectType(OrderedTag):
    SingleColumn = 1
    MultiColumn = 2

class DataTypes(StatementTag):
    Numeric = auto()
    String = auto()
    Date = auto()
    Timestamp = auto()


class TableCount(OrderedTag):
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Many = 6


class WhereType(OrderedTag):
    SingleWhereExpr = 1
    MultipleWhereExpr = 2


class ExprType(OrderedTag):
    SingleBinExpr = 1
    ArithExpr = 2
    ComplexExpr = 3


class GroupType(OrderedTag):
    UnconditionalGroup = 1
    ConditionalGroup = 2


class JoinConditions(OrderedTag):
    UnconditionalJoin = 1
    ConditionalJoin = 2

class JoinType(StatementTag):
    OuterJoin = auto()
    InnerJoin = auto()
    NaturalJoin = auto()
    CrossJoin = auto()
    LeftOuterJoin = auto()
    RightOuterJoin = auto()

class JoinTables(OrderedTag):
    SingleJoin = 1
    TwoJoin = 2
    MultiJoin = 3

class ExtraKeywords(StatementTag):
    Distinct = auto()
    Limit = auto()
    OrderBy = auto()
    ALL = auto()
    LIKE = auto()
    BETWEEN = auto()
    IS_NULL = auto()
    IN =  auto()
    EXISTS = auto()

class AggregateFuncs(StatementTag):
    MAX = auto()
    MIN = auto()
    SUM = auto()
    AVG = auto()
    COUNT = auto()


class StructureType(StatementTag):
    Compound = auto()
    Nested = auto()

class Nested(StatementTag):
    Zero = 0
    One = 1
    Two = 2
    Many = 3


class WindowFunction(StatementTag):
    PARTITION_BY = auto()
    WITH = auto()
    CASE = auto()
    WITH_RECURSIVE = auto()

