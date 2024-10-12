import pytest

from src.evaluator.str_visitor import StringVisitor
from tests.sql_test_data import TEST_SQLS
from tests.utils import parse, assert_sql_str_equal


@pytest.mark.parametrize("sql", TEST_SQLS)
def test_exprs(sql):
    ast = parse(sql)
    str_visitor = StringVisitor()
    assert_sql_str_equal(ast.accept(str_visitor), sql)


def test_parse_error():
    sql = "##"
    parse(sql)
