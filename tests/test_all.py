from src.prop_collectors.database_column import DatabaseColumn, STAR_COLUMN
from src.sql_parser.parser import SqlParser
from src.prop_collectors.graph_drawer import draw_graph
from src.prop_collectors.feature_extractor import SqlFeatureExtractor


def test_parser():
    sql = "SELECT count(*), Name, Country FROM singer"
    parser = SqlParser()
    ast = parser.parse(sql)
    ast.db_id = "concert_singer"
    draw_graph(ast, f'out/test_tree')
    stats_builder = SqlFeatureExtractor('tests/tables.json')
    features = stats_builder.extract_features(ast)
    assert features.table_set == {'singer'}
    assert features.fun_set == {'count'}
    assert STAR_COLUMN in features.col_set
    assert DatabaseColumn('singer', 'country', 'text') in features.col_set
    assert features.max_nest_level == 1
