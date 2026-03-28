import os
import pytest

from src.analyzer.letter_casing_transformer import LetterCasingTransformer
from src.analyzer.limit_fixing_transformer import FixPredLimitTransformer
from src.util.log_util import configure_logging

os.environ["LOG_LEVEL"] = "INFO"
configure_logging()

from src.analyzer.fix_finder import FixRule
from src.analyzer.rule_finder import RuleFinder
from src.configs.datasets import SPIDER_SMALL


@pytest.fixture(scope="module")
def finder():
    pass


def test_case_0():
    db_id = "allergy_1"
    pred_sql = "SELECT age FROM Student WHERE age < 19 ORDER BY age"
    gold_sql = "SELECT age, fname FROM Student WHERE age < 18"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.ExtraRow, FixRule.MissingColumn, FixRule.RowOrder}


def test_case_1():
    db_id = "concert_singer"
    pred_sql = "SELECT * FROM singer ORDER BY Song_release_year"
    gold_sql = "SELECT * FROM singer"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.RowOrder}


def test_case_2():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country FROM singer ORDER BY Singer_ID"
    gold_sql = "SELECT Country, Name FROM singer ORDER BY Singer_ID"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.ColumnOrder}


def test_case_3():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country FROM singer ORDER BY Singer_ID"
    gold_sql = "SELECT Name FROM singer ORDER BY Singer_ID"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.ExtraColumn}


def test_case_4():
    db_id = "concert_singer"
    pred_sql = "SELECT Name FROM singer ORDER BY Singer_ID"
    gold_sql = "SELECT Name FROM singer WHERE Age > 30 ORDER BY Singer_ID"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.ExtraRow}


def test_case_5():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country FROM singer ORDER BY Song_release_year"
    gold_sql = "SELECT Country, Name FROM singer"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.RowOrder, FixRule.ColumnOrder}


def test_case_6():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country FROM singer ORDER BY Song_release_year"
    gold_sql = "SELECT Name FROM singer"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.RowOrder, FixRule.ExtraColumn}


def test_case_7():
    db_id = "concert_singer"
    pred_sql = "SELECT Name FROM singer ORDER BY Song_release_year"
    gold_sql = "SELECT Name FROM singer WHERE Age > 30"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.RowOrder, FixRule.ExtraRow}


def test_case_8():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country, Age FROM singer ORDER BY Singer_ID"
    gold_sql = "SELECT Age, Name FROM singer ORDER BY Singer_ID"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.ColumnOrder, FixRule.ExtraColumn}


def test_case_9():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country FROM singer ORDER BY Singer_ID"
    gold_sql = "SELECT Country, Name FROM singer WHERE Age > 30 ORDER BY Singer_ID"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.ColumnOrder, FixRule.ExtraRow}


def test_case_10():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country FROM singer ORDER BY Singer_ID"
    gold_sql = "SELECT Name FROM singer WHERE Age > 30 ORDER BY Singer_ID"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.ExtraColumn, FixRule.ExtraRow}


def test_case_11():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country, Age FROM singer ORDER BY Song_release_year"
    gold_sql = "SELECT Age, Name FROM singer"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.RowOrder, FixRule.ColumnOrder, FixRule.ExtraColumn}


def test_case_12():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country FROM singer ORDER BY Song_release_year"
    gold_sql = "SELECT Country, Name FROM singer WHERE Age > 30"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.RowOrder, FixRule.ColumnOrder, FixRule.ExtraRow}


def test_case_13():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country FROM singer ORDER BY Song_release_year"
    gold_sql = "SELECT Name FROM singer WHERE Age > 30"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.RowOrder, FixRule.ExtraColumn, FixRule.ExtraRow}


def test_case_14():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country, Age FROM singer ORDER BY Singer_ID"
    gold_sql = "SELECT Age, Name FROM singer WHERE Age >= 30 ORDER BY Singer_ID"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.ColumnOrder, FixRule.ExtraColumn, FixRule.ExtraRow}


def test_case_15():
    db_id = "concert_singer"
    pred_sql = "SELECT Name, Country, Age FROM singer ORDER BY Song_release_year"
    gold_sql = "SELECT Age, Name FROM singer WHERE Age >= 30"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.RowOrder, FixRule.ColumnOrder, FixRule.ExtraColumn, FixRule.ExtraRow}


def test_case_16():
    db_id = "concert_singer"
    pred_sql = "SELECT * FROM singer LIMIT 2"
    gold_sql = "SELECT * FROM singer LIMIT 3"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixPredLimitTransformer()}


def test_case_17():
    db_id = "concert_singer"
    pred_sql = 'SELECT * FROM singer WHERE Song_Name = "lOvE"'
    gold_sql = 'SELECT * FROM singer WHERE Song_Name = "Love"'

    finder = RuleFinder(SPIDER_SMALL, {frozenset({LetterCasingTransformer()})}, set())

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {LetterCasingTransformer()}


def test_case_18():
    db_id = "concert_singer"
    pred_sql = "SELECT Name FROM singer"
    gold_sql = "SELECT Name, Country FROM singer"

    finder = RuleFinder(SPIDER_SMALL)

    rules = finder.find_rules(pred_sql, gold_sql, db_id)
    print(rules)
    assert rules == {FixRule.MissingColumn}
