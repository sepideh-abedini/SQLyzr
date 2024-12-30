import inspect
from itertools import chain, combinations
from typing import Iterable, List, Tuple, TypeVar


def get_all_subclasses(cls):
    subclasses = set()
    subclasses.update(cls.__subclasses__())
    subclasses = set(filter(lambda sc: not inspect.isabstract(sc), subclasses))
    for subclass in subclasses.copy():
        subclasses.update(get_all_subclasses(subclass))
    return subclasses


T = TypeVar('T')


def powerset(iterable: Iterable[T]) -> List[Tuple[T]]:
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))
