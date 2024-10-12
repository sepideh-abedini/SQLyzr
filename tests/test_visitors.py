import pytest

from src.visitor.tree_extractor import AstDiagramTreeExtractor
from tests.sql_test_data import TEST_SQLS
from tests.utils import parse


@pytest.mark.parametrize("sql", TEST_SQLS)
def test_exprs(sql):
    visitor = AstDiagramTreeExtractor()
    ast = parse(sql)
    ast.accept(visitor)
