from itertools import chain, combinations
from typing import Iterable, TypeVar, List, Tuple

T = TypeVar('T')


def powerset(iterable: Iterable[T]) -> List[Tuple[T]]:
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))
