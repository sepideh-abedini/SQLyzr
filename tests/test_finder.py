import pytest

from src.analyzer.fix_evaluator import FixFinder
from src.analyzer.fix_finder import FixRule
from src.configs.datasets import SPIDER_SMALL
from src.util.log_util import configure_logging

db_id = "allergy_1"


@pytest.fixture(scope="module")
def finder():
    configure_logging()


def test_case_1():
    pred_sql = "SELECT age FROM student ORDER BY age DESC"
    gold_sql = "SELECT age FROM student"
    rules = frozenset({FixRule.RowOrder})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_2():
    pred_sql = "SELECT fname FROM student"
    gold_sql = "SELECT fname, lname FROM student"
    rules = frozenset({FixRule.MissingColumn})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_3():
    pred_sql = "SELECT fname, lname, age FROM student"
    gold_sql = "SELECT fname, lname FROM student"
    rules = frozenset({FixRule.ExtraColumn})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_4():
    pred_sql = "SELECT lname, fname FROM student"
    gold_sql = "SELECT fname, lname FROM student"
    rules = frozenset({FixRule.ColumnOrder})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_5():
    pred_sql = "SELECT fname FROM student WHERE age > 20"
    gold_sql = "SELECT fname FROM student WHERE age > 18"
    rules = frozenset({FixRule.MissingRow})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_6():
    pred_sql = "SELECT fname FROM student WHERE age > 18"
    gold_sql = "SELECT fname FROM student WHERE age > 20"
    rules = frozenset({FixRule.ExtraRow})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_7():
    # RowOrder + ColumnOrder
    pred_sql = "SELECT lname, fname FROM student ORDER BY age DESC"
    gold_sql = "SELECT fname, lname FROM student"
    rules = frozenset({FixRule.RowOrder, FixRule.ColumnOrder})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_8():
    # RowOrder + MissingColumn
    pred_sql = "SELECT fname FROM student ORDER BY age DESC"
    gold_sql = "SELECT fname, lname FROM student"
    rules = frozenset({FixRule.RowOrder, FixRule.MissingColumn})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_9():
    # RowOrder + ExtraColumn
    pred_sql = "SELECT fname, lname, age FROM student ORDER BY age DESC"
    gold_sql = "SELECT fname, lname FROM student"
    rules = frozenset({FixRule.RowOrder, FixRule.ExtraColumn})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_10():
    # RowOrder + MissingRow
    pred_sql = "SELECT fname FROM student WHERE age > 20 ORDER BY age DESC"
    gold_sql = "SELECT fname FROM student WHERE age > 18"
    rules = frozenset({FixRule.RowOrder, FixRule.MissingRow})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    # Note: If RowOrder is allowed, it means we don't care about order.
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_11():
    # RowOrder + ExtraRow
    pred_sql = "SELECT fname FROM student WHERE age > 18 ORDER BY age DESC"
    gold_sql = "SELECT fname FROM student WHERE age > 20"
    rules = frozenset({FixRule.RowOrder, FixRule.ExtraRow})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_12():
    # ColumnOrder + MissingRow
    pred_sql = "SELECT lname, fname FROM student WHERE age > 20"
    gold_sql = "SELECT fname, lname FROM student WHERE age > 18"
    rules = frozenset({FixRule.ColumnOrder, FixRule.MissingRow})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_13():
    # ColumnOrder + ExtraRow
    pred_sql = "SELECT lname, fname FROM student WHERE age > 18"
    gold_sql = "SELECT fname, lname FROM student WHERE age > 20"
    rules = frozenset({FixRule.ColumnOrder, FixRule.ExtraRow})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_14():
    # ColumnOrder + MissingColumn
    pred_sql = "SELECT lname FROM student"
    gold_sql = "SELECT fname, lname FROM student"
    rules = frozenset({FixRule.ColumnOrder, FixRule.MissingColumn})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_15():
    # ColumnOrder + ExtraColumn
    pred_sql = "SELECT lname, fname, age FROM student"
    gold_sql = "SELECT fname, lname FROM student"
    rules = frozenset({FixRule.ColumnOrder, FixRule.ExtraColumn})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_16():
    # MissingRow + MissingColumn
    pred_sql = "SELECT fname FROM student WHERE age > 20"
    gold_sql = "SELECT fname, lname FROM student WHERE age > 18"
    rules = frozenset({FixRule.MissingRow, FixRule.MissingColumn})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_17():
    # MissingRow + ExtraColumn
    pred_sql = "SELECT fname, lname, age FROM student WHERE age > 20"
    gold_sql = "SELECT fname, lname FROM student WHERE age > 18"
    rules = frozenset({FixRule.MissingRow, FixRule.ExtraColumn})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_18():
    # ExtraRow + MissingColumn
    pred_sql = "SELECT fname FROM student WHERE age > 18"
    gold_sql = "SELECT fname, lname FROM student WHERE age > 20"
    rules = {FixRule.ExtraRow, FixRule.MissingColumn}
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    # assert finder.evaluate(db_id, pred_sql, gold_sql)


def test_case_19():
    # ExtraRow + ExtraColumn
    pred_sql = "SELECT fname, lname, age FROM student WHERE age > 18"
    gold_sql = "SELECT fname, lname FROM student WHERE age > 20"
    rules = frozenset({FixRule.ExtraRow, FixRule.ExtraColumn})
    finder = FixFinder(SPIDER_SMALL, frozenset(), rules)
    assert not finder.evaluate_strict(db_id, pred_sql, gold_sql)
    assert finder.evaluate(db_id, pred_sql, gold_sql)
