from collections import defaultdict
from typing import Optional

from src.analyzer.fix_finder import MapProp


def match_row(r1: list[str], r2: list[str], props: set[MapProp]) -> Optional[dict[int, int]]:
    if MapProp.Injective in props:
        left = r1
        right = r2
    elif MapProp.Surjective in props:
        left = r2
        right = r1
    else:
        raise RuntimeError("The row mapping should be either Injective or Surjective")

    if MapProp.Injective in props and MapProp.Surjective in props:
        if len(left) != len(right):
            return None

    val_to_idx_right = defaultdict(list)
    for j, val_right in enumerate(right):
        val_to_idx_right[val_right].append(j)

    matching = dict()
    for i, val_left in enumerate(left):
        if val_left not in val_to_idx_right:
            return None
        ids = val_to_idx_right[val_left]
        if len(ids) == 0:
            return None
        matching[i] = val_to_idx_right[val_left].pop()
    assert len(matching) == len(left)
    return matching


def match_row_monotone(r1: list[str], r2: list[str], props: set[MapProp]) -> Optional[dict[int, int]]:
    if MapProp.Injective in props:
        left = r1
        right = r2
    elif MapProp.Surjective in props:
        left = r2
        right = r1
    else:
        raise RuntimeError("The row mapping should be either Injective or Surjective")

    if MapProp.Injective in props and MapProp.Surjective in props:
        if len(left) != len(right):
            return None

    val_to_idx_right = defaultdict(list)
    for j, val_right in enumerate(right):
        val_to_idx_right[val_right].append(j)

    for v in val_to_idx_right:
        val_to_idx_right[v].sort()

    matching = {}
    last_j = -1

    for i, val_left in enumerate(left):
        if val_left not in val_to_idx_right:
            return None
        ids = val_to_idx_right[val_left]

        k = 0
        while k < len(ids) and ids[k] <= last_j:
            k += 1
        if k == len(ids):
            return None

        matching[i] = ids.pop(k)
        last_j = matching[i]
    return matching


def match_row_mon_prop(r1: list[str], r2: list[str], props: set[MapProp]):
    mono = MapProp.Monotonic in props
    if mono:
        return match_row_monotone(r1, r2, props)
    else:
        return match_row(r1, r2, props)


def match_row_prop(r1: list[str], r2: list[str], props: set[MapProp]) -> Optional[dict[int, int]]:
    return match_row_mon_prop(r1, r2, props)


def check_row_match(r1: list[str], r2: list[str], m: dict[int, int], props: set[MapProp]):
    if MapProp.Injective in props:
        left = r1
        right = r2
    elif MapProp.Surjective in props:
        left = r2
        right = r1
    else:
        raise RuntimeError("The row mapping should be either Injective or Surjective")

    if MapProp.Injective in props and MapProp.Surjective in props:
        if len(left) != len(right):
            return None

    for i, j in m.items():
        if left[i] != right[j]:
            return False
    return True
