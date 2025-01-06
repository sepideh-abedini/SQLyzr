from enum import auto

from src.cat.tags.sql_tag import SqlTag


class JoinType(SqlTag):
    OuterJoin = auto()
    InnerJoin = auto()
    NaturalJoin = auto()
    CrossJoin = auto()
    LeftOuterJoin = auto()
    RightOuterJoin = auto()
