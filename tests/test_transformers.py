from typing import List, Type

import pytest
from assertpy import assert_that

from src.configs.datasets import SPIDER_SMALL
from src.eval.dataset_config import DatasetConfig
from src.parse.parser import SqlParser
from src.rel.result_matcher import IgnoreListOrderMatcher, IgnoreColOrderMatcher, ExtraColumnsMatcher, \
    ExtraTupleMatcher, MissingColumnsMatcher
from src.rel.sql_data import SqlInputData
from src.rel.sql_transformer import SqlTransformer, FixPredLimitTransformer, LetterCasingTransformer
from src.rel.transformer_detector import TransformerDetector
from src.util.log_util import configure_logging


def main():
    print("Hello")


if __name__ == '__main__':
    main()


def assert_sql_parsable(sql: str):
    parser = SqlParser()
    ast = parser.parse(sql)
    assert_that(ast).is_not_none()


@pytest.mark.parametrize(
    "processors, pred_sql, gold_sql, db_id, expected_trs",
    [
        (
                [IgnoreListOrderMatcher()],
                'SELECT * FROM singer ORDER BY Song_release_year',
                'SELECT * FROM singer',
                "concert_singer",
                [IgnoreListOrderMatcher]
        ),
        (
                [IgnoreColOrderMatcher()],
                'SELECT Name, Country FROM singer ORDER BY Singer_ID',
                'SELECT Country, Name FROM singer ORDER BY Singer_ID',
                "concert_singer",
                [IgnoreColOrderMatcher]
        ),
        (
                [ExtraColumnsMatcher()],
                'SELECT Name, Country FROM singer ORDER BY Singer_ID',
                'SELECT Name FROM singer ORDER BY Singer_ID',
                "concert_singer",
                [ExtraColumnsMatcher]
        ),
        (
                [ExtraTupleMatcher()],
                'SELECT Name FROM singer ORDER BY Singer_ID',
                'SELECT Name FROM singer WHERE Age > 30 ORDER BY Singer_ID',
                "concert_singer",
                [ExtraTupleMatcher]
        ),

        (
                [IgnoreListOrderMatcher(), IgnoreColOrderMatcher()],
                'SELECT Name, Country FROM singer ORDER BY Song_release_year',
                'SELECT Country, Name FROM singer',
                "concert_singer",
                [IgnoreListOrderMatcher, IgnoreColOrderMatcher]
        ),
        (
                [IgnoreListOrderMatcher(), ExtraColumnsMatcher()],
                'SELECT Name, Country FROM singer ORDER BY Song_release_year',
                'SELECT Name FROM singer',
                "concert_singer",
                [IgnoreListOrderMatcher, ExtraColumnsMatcher]
        ),
        (
                [IgnoreListOrderMatcher(), ExtraTupleMatcher()],
                'SELECT Name FROM singer ORDER BY Song_release_year',
                'SELECT Name FROM singer WHERE Age > 30',
                "concert_singer",
                [IgnoreListOrderMatcher, ExtraTupleMatcher]
        ),
        (
                [IgnoreColOrderMatcher(), ExtraColumnsMatcher()],
                'SELECT Name, Country, Age FROM singer ORDER BY Singer_ID',
                'SELECT Age, Name FROM singer ORDER BY Singer_ID',
                "concert_singer",
                [IgnoreColOrderMatcher, ExtraColumnsMatcher]
        ),
        (
                [IgnoreColOrderMatcher(), ExtraTupleMatcher()],
                'SELECT Name, Country FROM singer ORDER BY Singer_ID',
                'SELECT Country, Name FROM singer WHERE Age > 30 ORDER BY Singer_ID',
                "concert_singer",
                [IgnoreColOrderMatcher, ExtraTupleMatcher]
        ),
        (
                [ExtraColumnsMatcher(), ExtraTupleMatcher()],
                'SELECT Name, Country FROM singer ORDER BY Singer_ID',
                'SELECT Name FROM singer WHERE Age > 30 ORDER BY Singer_ID',
                "concert_singer",
                [ExtraColumnsMatcher, ExtraTupleMatcher]
        ),

        (
                [IgnoreListOrderMatcher(), IgnoreColOrderMatcher(), ExtraColumnsMatcher()],
                'SELECT Name, Country, Age FROM singer ORDER BY Song_release_year',
                'SELECT Age, Name FROM singer',
                "concert_singer",
                [IgnoreListOrderMatcher, IgnoreColOrderMatcher, ExtraColumnsMatcher]
        ),
        (
                [IgnoreListOrderMatcher(), IgnoreColOrderMatcher(), ExtraTupleMatcher()],
                'SELECT Name, Country FROM singer ORDER BY Song_release_year',
                'SELECT Country, Name FROM singer WHERE Age > 30',
                "concert_singer",
                [IgnoreListOrderMatcher, IgnoreColOrderMatcher, ExtraTupleMatcher]
        ),
        (
                [IgnoreListOrderMatcher(), ExtraColumnsMatcher(), ExtraTupleMatcher()],
                'SELECT Name, Country FROM singer ORDER BY Song_release_year',
                'SELECT Name FROM singer WHERE Age > 30',
                "concert_singer",
                [IgnoreListOrderMatcher, ExtraColumnsMatcher, ExtraTupleMatcher]
        ),
        (
                [IgnoreColOrderMatcher(), ExtraColumnsMatcher(), ExtraTupleMatcher()],
                'SELECT Name, Country, Age FROM singer ORDER BY Singer_ID',
                'SELECT Age, Name FROM singer WHERE Age >= 30 ORDER BY Singer_ID',
                "concert_singer",
                [IgnoreColOrderMatcher, ExtraColumnsMatcher, ExtraTupleMatcher]
        ),

        (
                [IgnoreListOrderMatcher(), IgnoreColOrderMatcher(), ExtraColumnsMatcher(), ExtraTupleMatcher()],
                'SELECT Name, Country, Age FROM singer ORDER BY Song_release_year',
                'SELECT Age, Name FROM singer WHERE Age >= 30',
                "concert_singer",
                [IgnoreListOrderMatcher, IgnoreColOrderMatcher, ExtraColumnsMatcher, ExtraTupleMatcher]
        ),
        # Other Transformers
        (
                [FixPredLimitTransformer()],
                "SELECT * FROM singer LIMIT 2",
                "SELECT * FROM singer LIMIT 3",
                "concert_singer",
                [FixPredLimitTransformer]
        ),
        (
                [LetterCasingTransformer()],
                'SELECT * FROM singer WHERE Song_Name = "lOvE"',
                'SELECT * FROM singer WHERE Song_Name = "Love"',
                "concert_singer",
                [LetterCasingTransformer]
        ),

        # Missing Column Transformer
        (
                [MissingColumnsMatcher()],
                'SELECT Name FROM singer',
                'SELECT Name, Country FROM singer',
                "concert_singer",
                [MissingColumnsMatcher]
        ),
    ],
)
def test_transformer_detector(processors: List[SqlTransformer], pred_sql: str, gold_sql: str, db_id: str,
                              expected_trs: List[Type[SqlTransformer]]):
    configure_logging()

    assert_sql_parsable(pred_sql)
    assert_sql_parsable(gold_sql)

    ds_conf = DatasetConfig(
        dataset_dir="tests/test_data",
        test_file="data.test.json",
        gold_file="data.test.gold.txt",
        train_file="data.train.json",
        tables_file="tables.json",
        db_dir="database"
    )
    detector = TransformerDetector(ds_conf, processors)

    pred = SqlInputData(db_id, pred_sql)
    gold = SqlInputData(db_id, gold_sql)

    trs = detector.find_working_sub_sync(pred, gold)

    assert_that(trs).is_not_none()

    assert_that(trs, "Expected SQL results don't match!").is_not_empty()

    actual_trs = [type(t).__name__ for t in trs]
    expected_trs = [t.__name__ for t in expected_trs]
    assert_that(actual_trs).is_equal_to(expected_trs)
