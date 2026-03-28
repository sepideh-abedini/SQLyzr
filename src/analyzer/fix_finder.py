from enum import Enum, auto
from itertools import chain, combinations


class MapProp(Enum):
    Injective = auto()
    Surjective = auto()
    Monotonic = auto()

    @staticmethod
    def all():
        return {
            MapProp.Injective,
            MapProp.Surjective,
            MapProp.Monotonic,
        }

    def reverse(self) -> 'MapProp':
        if self == MapProp.Monotonic:
            return MapProp.Monotonic
        elif self == MapProp.Surjective:
            return MapProp.Injective
        elif self == MapProp.Injective:
            return MapProp.Surjective
        else:
            raise RuntimeError("Unknown MapProp.")

    @staticmethod
    def reverse_set(props: set['MapProp']) -> set['MapProp']:
        return set(map(lambda p: p.reverse(), props))


class FixRule(Enum):
    MissingColumn = ("MissingColumn", "The predicted SQL query should be modified to include missing columns.")
    ExtraColumn = ("ExtraColumn",
                   "The predicted SQL query should be modified to remove the extra columns in the output.")
    ColumnOrder = ("ColumnOrder",
                   "The predicted SQL query should be modified to fix the order of columns in the result set.")
    MissingRow = ("MissingRow", "The predicted SQL query has missing rows.!")
    ExtraRow = ("ExtraRow", "The predicted SQL should be modified to remove extra rows in the result set.")
    RowOrder = ("RowOrder", "The predicted SQL query should be modified to fix the order of rows in the result set.")

    def __init__(self, code: str, msg: str):
        self.code = code
        self.msg = msg

    @classmethod
    def all_subsets(cls) -> frozenset[frozenset['FixRule']]:
        incompatible_rules = [
            {cls.MissingRow, cls.ExtraRow},
            {cls.MissingColumn, cls.ExtraColumn},
            {cls.MissingRow}
        ]
        values = list(FixRule)
        all_sets = chain.from_iterable(combinations(values, r) for r in range(len(values) + 1))
        return frozenset(
            subset for subset in all_sets
            if not any(set(rule_pair).issubset(subset) for rule_pair in incompatible_rules)
        )


def get_row_props(rules: set[FixRule]) -> set[MapProp]:
    props = MapProp.all()
    if FixRule.MissingColumn in rules:
        props.remove(MapProp.Surjective)
    if FixRule.ExtraColumn in rules:
        props.remove(MapProp.Injective)
    if FixRule.ColumnOrder in rules:
        props.remove(MapProp.Monotonic)
    return props


def get_rs_props(rules: set[FixRule]) -> set[MapProp]:
    props = MapProp.all()
    if FixRule.MissingRow in rules:
        props.remove(MapProp.Surjective)
    if FixRule.ExtraRow in rules:
        props.remove(MapProp.Injective)
    if FixRule.RowOrder in rules:
        props.remove(MapProp.Monotonic)
    return props
