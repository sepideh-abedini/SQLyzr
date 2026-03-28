from src.analyzer.fix_finder import MapProp
from src.analyzer.list_matcher import match_list_of_list_full_prop


def test_case_1():
    left = [["a"]]
    right = [["a"]]
    rs_props = {MapProp.Surjective}
    row_props = {MapProp.Surjective}
    m = match_list_of_list_full_prop(left, right, rs_props, row_props)
    assert m is not None


def test_case_2():
    left = [["a"]]
    right = [["a"]]
    rs_props = {MapProp.Injective}
    row_props = {MapProp.Injective}
    m = match_list_of_list_full_prop(left, right, rs_props, row_props)
    assert m is not None


def test_case_3():
    left = [["a"]]
    right = [["a"], ["b"]]
    rs_props = {MapProp.Injective}
    row_props = {MapProp.Injective}
    m = match_list_of_list_full_prop(left, right, rs_props, row_props)
    assert m is not None


def test_case_4():
    left = [["a"]]
    right = [["a", "b"]]
    rs_props = {MapProp.Injective}
    row_props = {MapProp.Injective}
    m = match_list_of_list_full_prop(left, right, rs_props, row_props)
    assert m is not None


def test_case_5():
    left = [["a", "b"]]
    right = [["a"]]
    rs_props = {MapProp.Injective}
    row_props = {MapProp.Surjective}
    m = match_list_of_list_full_prop(left, right, rs_props, row_props)
    assert m is not None


def test_case_6():
    left = [["a"], ["b"]]
    right = [["a"]]
    rs_props = {MapProp.Surjective}
    row_props = {MapProp.Injective}
    m = match_list_of_list_full_prop(left, right, rs_props, row_props)
    assert m is not None


def test_case_7():
    left = [["a", "c"], ["b", "d"], ["e", "f"]]
    right = [["b"], ["a"]]
    rs_props = {MapProp.Surjective}
    row_props = {MapProp.Surjective}
    m = match_list_of_list_full_prop(left, right, rs_props, row_props)
    assert m is not None


def test_case_8():
    left = [["a"], ["b"], ["e"]]
    right = [["d", "b"], ["c", "a"]]
    # left = [["b"]]
    # right = [["d", "b"]]
    rs_props = {MapProp.Surjective}
    row_props = {MapProp.Injective}
    m = match_list_of_list_full_prop(left, right, rs_props, row_props)
    assert m is not None


def test_case_9():
    left = [['Tracy'], ['Shiela'], ['Dinesh'], ['Paul']]
    right = [['Shiela', 'Jones'], ['Paul', 'Gompers']]
    rs_props = {MapProp.Surjective}
    row_props = {MapProp.Injective}
    m = match_list_of_list_full_prop(left, right, rs_props, row_props)
    assert m is not None
