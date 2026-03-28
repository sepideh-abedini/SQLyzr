from src.analyzer.fix_finder import MapProp
from src.analyzer.row_matcher import match_row_mon_prop


def test_case_1():
    left = ["a", "b"]
    right = ["a", "b", "c"]
    props = {MapProp.Injective}
    assert match_row_mon_prop(left, right, props) is not None


def test_case_1_2():
    left = ["a", "b", "c"]
    right = ["a", "b", "c"]
    props = {MapProp.Injective}
    assert match_row_mon_prop(left, right, props) is not None


def test_case_2():
    left = ["a", "a", "b"]
    right = ["a", "b"]
    props = {MapProp.Injective}
    assert match_row_mon_prop(left, right, props) is None


def test_case_3():
    left = ["a", "b", "c"]
    right = ["a", "c"]
    props = {MapProp.Surjective}
    assert match_row_mon_prop(left, right, props) is not None


def test_case_4():
    left = ["a", "b"]
    right = ["a", "b", "c"]
    props = {MapProp.Surjective}
    assert match_row_mon_prop(left, right, props) is None


def test_case_4_1():
    left = ["a", "b", "c"]
    right = ["a", "b", "c"]
    props = {MapProp.Surjective}
    assert match_row_mon_prop(left, right, props) is not None


def test_case_5():
    left = ["a", "b", "c"]
    right = ["a", "b", "c"]
    props = {MapProp.Monotonic, MapProp.Injective}
    assert match_row_mon_prop(left, right, props) is not None


def test_case_6():
    left = ["c", "b", "a"]
    right = ["a", "b", "c"]
    props = {MapProp.Monotonic, MapProp.Injective}
    assert match_row_mon_prop(left, right, props) is None


def test_case_7():
    left = ["a", "b", "c"]
    right = ["a", "b", "c"]
    props = {MapProp.Injective, MapProp.Surjective}
    assert match_row_mon_prop(left, right, props) is not None


def test_case_8():
    left = ["a", "b", "c"]
    right = ["a", "c"]
    props = {MapProp.Injective, MapProp.Surjective}
    assert match_row_mon_prop(left, right, props) is None


def test_case_9():
    left = ["a", "x", "b", "c", "y"]
    right = ["a", "b", "c"]
    props = {MapProp.Surjective, MapProp.Monotonic}
    assert match_row_mon_prop(left, right, props) is not None


def test_case_10():
    left = ["a", "b", "c"]
    right = ["c", "a"]
    props = {MapProp.Surjective, MapProp.Monotonic}
    assert match_row_mon_prop(left, right, props) is None


def test_case_11():
    left = ["a", "b", "c"]
    right = ["a", "x", "y", "b", "c"]
    props = {MapProp.Injective, MapProp.Monotonic}
    assert match_row_mon_prop(left, right, props) is not None


def test_case_12():
    left = ["a", "a", "b"]
    right = ["a", "b"]
    props = {MapProp.Injective, MapProp.Monotonic}
    assert match_row_mon_prop(left, right, props) is None


def test_case_13():
    left = ["a", "b", "c"]
    right = ["a", "b", "c"]
    props = {MapProp.Injective, MapProp.Surjective, MapProp.Monotonic}
    assert match_row_mon_prop(left, right, props) is not None


def test_case_14():
    left = ["a", "b", "c"]
    right = ["a", "c"]
    props = {MapProp.Injective, MapProp.Surjective, MapProp.Monotonic}
    assert match_row_mon_prop(left, right, props) is None


def test_case_15():
    left = ["a", "b", "a"]
    right = ["a", "a", "b"]
    props = {MapProp.Injective, MapProp.Surjective}
    assert match_row_mon_prop(left, right, props) is not None
