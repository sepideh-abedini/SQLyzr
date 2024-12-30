from src.prop_collectors.keyword_collector import KeywordCollector
from src.prop_collectors.column_collector import ColumnCollector
from src.dbutil.schema_repo import DatabaseSchemaRepo
from src.sql_parser.node import SqlAstNode
from src.prop_collectors.terminal_collector import TerminalCollector
from src.prop_collectors.join_tables_collector import JoinTablesCollector
from src.prop_collectors.tables_collector import TablesCollector
from src.prop_collectors.nest_level_collector import NestLevelCollector
from src.prop_collectors.sql_features import SqlFeatures
from src.visitor.tree_extractor import AstDiagramTreeExtractor


class SqlFeatureExtractor:
    db_repo: DatabaseSchemaRepo

    def __init__(self, tables_json_path: str):
        self.db_repo = DatabaseSchemaRepo(tables_json_path)

    def extract_features(self, ast: SqlAstNode) -> SqlFeatures:
        db_schema = self.db_repo.dbs[ast.db_id]

        column_collector = ColumnCollector(db_schema)
        collectors = [column_collector,
                      JoinTablesCollector(),
                      TablesCollector(),
                      TerminalCollector(),
                      NestLevelCollector(),
                      KeywordCollector()]

        features = SqlFeatures()
        for collector in collectors:
            features += ast.accept(collector)
        tree = ast.accept(AstDiagramTreeExtractor())
        features.max_tree_size = tree.get_num_nodes()
        features.max_tree_height = tree.get_height()
        return features
