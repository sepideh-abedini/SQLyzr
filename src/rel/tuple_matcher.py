from dataclasses import dataclass
from typing import Tuple, List, Iterable

from loguru import logger

MAX_PERM = 1_000_000


@dataclass
class TupleMatchConf:
    ignore_col_order: bool = False
    ignore_extra_col: bool = False
    ignore_tuples_order: bool = False
    ignore_extra_tuple: bool = False
    ignore_missing_col: bool = False

    def __add__(self, other: 'TupleMatchConf'):
        if not isinstance(other, TupleMatchConf):
            raise RuntimeError(f"Invalid operand type {type(other)}")
        return TupleMatchConf(
            ignore_col_order=self.ignore_col_order or other.ignore_col_order,
            ignore_extra_col=self.ignore_extra_col or other.ignore_extra_col,
            ignore_tuples_order=self.ignore_tuples_order or other.ignore_tuples_order,
            ignore_extra_tuple=self.ignore_extra_tuple or other.ignore_extra_tuple,
            ignore_missing_col=self.ignore_missing_col or other.ignore_missing_col
        )


@dataclass
class TupleWrapper:
    t: Tuple

    def match(self, gold: "TupleWrapper", conf: TupleMatchConf) -> bool:
        if conf.ignore_col_order:
            if conf.ignore_extra_col:
                return frozenset(gold.t).issubset(frozenset(self.t))
            else:
                return frozenset(gold.t) == frozenset(self.t)
        else:
            if conf.ignore_extra_col:
                return TupleWrapper.match_with_extra_col(self, gold)
            elif conf.ignore_missing_col:
                return TupleWrapper.match_with_extra_col(gold, self)
            else:
                return self.t == gold.t

    @staticmethod
    def match_with_extra_col(pred: 'TupleWrapper', gold: "TupleWrapper") -> bool:
        if len(pred.t) < len(gold.t):
            return False
        j = 0
        for i in range(len(pred.t)):
            if j >= len(gold.t):
                return True
            if pred.t[i] == gold.t[j]:
                j += 1
        if j >= len(gold.t):
            return True
        return False


@dataclass
class ListWrapper:
    l: List[TupleWrapper]

    @staticmethod
    def wrap(l: Iterable[Tuple]):
        return ListWrapper(list(map(lambda t: TupleWrapper(t), l)))

    def __len__(self):
        return len(self.l)

    def __getitem__(self, i):
        return self.l[i]

    def __iter__(self):
        return iter(self.l)

    def includes(self, gi: TupleWrapper, conf: TupleMatchConf) -> bool:
        for pi in self:
            if pi.match(gi, conf):
                return True
        return False

    def match(self, gold: "ListWrapper", conf: TupleMatchConf) -> bool:
        if conf.ignore_extra_tuple is False:
            if len(gold) != len(self):
                return False
        if conf.ignore_tuples_order:
            if len(self) * len(gold) > MAX_PERM:
                logger.warning(f"Too many permutations: {len(self)} * {len(gold)} > {MAX_PERM}")
                return False
            for gi in gold:
                if self.includes(gi, conf) is False:
                    return False
            return True
        else:
            if len(self) < len(gold):
                return False
            j = 0
            for i in range(len(self)):
                if j >= len(gold):
                    return True
                pi = self[i]
                gj = gold[j]
                if pi.match(gj, conf):
                    j += 1
            if j >= len(gold):
                return True
            return False
