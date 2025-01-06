from enum import auto

from src.cat.tags.sql_tag import SqlTag, OrderedTag


class TableCount(OrderedTag):
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Many = 6










class AggregateFuncs(SqlTag):
    MAX = auto()
    MIN = auto()
    SUM = auto()
    AVG = auto()
    COUNT = auto()





class WindowFunction(SqlTag):
    PARTITION_BY = auto()
    WITH = auto()
    CASE = auto()
    WITH_RECURSIVE = auto()
