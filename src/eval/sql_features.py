from dataclasses import dataclass, replace, field
from typing import List, Set

from src.eval.database_column import DatabaseColumn
from src.parse.visitor.visitor_result import MergeableVisitorResult


@dataclass
class SqlFeatures(MergeableVisitorResult):
    id: int = None
    join_tables_count_list: List[int] = field(
        default_factory=list)  # Number of tables in each JOIN clause
    table_set: Set[str] = field(default_factory=set)
    fun_set: Set[str] = field(default_factory=set)
    set_op_set: Set[str] = field(default_factory=set)
    bin_op_set: Set[str] = field(default_factory=set)
    col_set: Set[DatabaseColumn] = field(default_factory=set)
    has_order_by: bool = False
    has_limit: bool = False
    has_group: bool = False
    has_between: bool = False
    max_nest_level: int = 0
    max_tree_size: int = 0
    max_tree_height: int = 0
    max_where_expr_size: int = 0

    def merge(self, other: 'SqlFeatures') -> 'SqlFeatures':
        if not isinstance(other, SqlFeatures):
            raise RuntimeError(f"Invalid type to merge with sql properties:{type(other)}")
        kw = {}
        for a in dir(self):
            if not callable(getattr(self, a)) and not a.startswith("_"):
                self_attr = getattr(self, a)
                other_attr = getattr(other, a)
                combined = self_attr
                if a.startswith("max_"):
                    combined = max(combined, other_attr)
                if a.startswith("has_"):
                    combined |= other_attr
                if a.endswith("_list"):
                    combined += other_attr
                if a.endswith("_set"):
                    combined = combined.union(other_attr)
                kw[a] = combined
        return replace(self, **kw)
