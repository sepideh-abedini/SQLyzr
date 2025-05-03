from typing import Tuple, List

import pytest
from assertpy import assert_that

from src.rel.tuple_matcher import TupleMatchConf, TupleWrapper, ListWrapper


@pytest.mark.parametrize(
    "pred, gold, conf",
    [
        ((), (), TupleMatchConf),
        ((1, 2), (1, 2), TupleMatchConf()),
        ((1, 2), (2, 1), TupleMatchConf(ignore_col_order=True)),
        ((1, 2, 3), (1, 2), TupleMatchConf(ignore_extra_col=True)),
        ((1, 2, 3), (2, 1), TupleMatchConf(ignore_extra_col=True, ignore_col_order=True))
    ],
)
def test_match(pred: Tuple, gold: Tuple, conf: TupleMatchConf):
    pt = TupleWrapper(pred)
    gt = TupleWrapper(gold)

    assert_that(pt.match(gt, conf)).is_true()


@pytest.mark.parametrize(
    "pred, gold, conf",
    [
        ((1, 2), (2, 3), TupleMatchConf()),
        ((1, 2, 3), (1, 2), TupleMatchConf(ignore_col_order=True)),
        ((1, 2), (1, 2, 3), TupleMatchConf(ignore_col_order=True)),
        ((1, 2, 3), (2, 1), TupleMatchConf(ignore_extra_col=True)),
        ((1, 2), (1, 2, 3), TupleMatchConf(ignore_extra_col=True)),
        ((1, 2), (2, 3), TupleMatchConf(ignore_extra_col=True, ignore_col_order=True))
    ],
)
def test_no_match(pred: Tuple, gold: Tuple, conf: TupleMatchConf):
    pt = TupleWrapper(pred)
    gt = TupleWrapper(gold)

    assert_that(pt.match(gt, conf)).is_false()


@pytest.mark.parametrize(
    "pred, gold, conf",
    [
        ([], [], TupleMatchConf()),
        ([1], [1], TupleMatchConf()),
        ([1, 2], [2, 1], TupleMatchConf(ignore_tuples_order=True)),
        ([1, 2, 3], [1, 2], TupleMatchConf(ignore_extra_tuple=True)),
        ([1, 2, 3], [1, 3], TupleMatchConf(ignore_extra_tuple=True)),
        ([1, 2, 3], [2, 1], TupleMatchConf(ignore_tuples_order=True, ignore_extra_tuple=True)),
    ],
)
def test_list_match(pred: List[Tuple], gold: List[Tuple], conf: TupleMatchConf):
    pt = ListWrapper.wrap(pred)
    gt = ListWrapper.wrap(gold)

    assert_that(pt.match(gt, conf)).is_true()


@pytest.mark.parametrize(
    "pred, gold, conf",
    [
        ([1], [2], TupleMatchConf()),
        ([1, 2, 3], [1, 2], TupleMatchConf(ignore_tuples_order=True)),
        ([1, 2], [1, 2, 3], TupleMatchConf(ignore_tuples_order=True)),
        ([3, 2, 1], [1, 2], TupleMatchConf(ignore_extra_tuple=True)),
        ([1, 2], [1, 2, 3], TupleMatchConf(ignore_extra_tuple=True)),
        ([1, 2], [2, 3], TupleMatchConf(ignore_extra_tuple=True, ignore_tuples_order=True)),
    ],
)
def test_list_no_match(pred: List[Tuple], gold: List[Tuple], conf: TupleMatchConf):
    pt = ListWrapper.wrap(pred)
    gt = ListWrapper.wrap(gold)

    assert_that(pt.match(gt, conf)).is_false()


@pytest.mark.parametrize(
    "pred, gold, conf",
    [
        ([(2, 1, 3), (6, 7, 8), (5, 3, 4)], [(3, 4), (1, 2)],
         TupleMatchConf(ignore_col_order=True, ignore_extra_col=True, ignore_tuples_order=True,
                        ignore_extra_tuple=True)),
        ([(1, 3, 2), (6, 7, 8), (5, 3, 4)], [(3, 4), (1, 2)],
         TupleMatchConf(ignore_col_order=False, ignore_extra_col=True, ignore_tuples_order=True,
                        ignore_extra_tuple=True)),
        ([(2, 1, 3), (6, 7, 8), (5, 3, 4)], [(3, 4, 5), (1, 2, 3)],
         TupleMatchConf(ignore_col_order=True, ignore_extra_col=False, ignore_tuples_order=True,
                        ignore_extra_tuple=True)),
        ([(2, 1, 3), (6, 7, 8), (5, 3, 4)], [(1, 2), (3, 4)],
         TupleMatchConf(ignore_col_order=True, ignore_extra_col=True, ignore_tuples_order=False,
                        ignore_extra_tuple=True)),
        ([(2, 1, 3), (6, 7, 8), (5, 3, 4)], [(3, 4), (1, 2), (7, 8)],
         TupleMatchConf(ignore_col_order=True, ignore_extra_col=True, ignore_tuples_order=True,
                        ignore_extra_tuple=False)),
    ],
)
def test_row_and_col_comb(pred: List[Tuple], gold: List[Tuple], conf: TupleMatchConf):
    pt = ListWrapper.wrap(pred)
    gt = ListWrapper.wrap(gold)

    assert_that(pt.match(gt, conf)).is_true()
