from src.prop_collectors.sql_features import SqlFeatures
from src.batch.exporter import BatchAstExporterProcessor, T
from src.prop_collectors.feature_extractor import SqlFeatureExtractor
from src.sql_parser.node import SqlAstNode


class BatchFeatureExporter(BatchAstExporterProcessor):
    """Input: List[SqlAstNode]
       Output: CSV[SqlProperties]
    """

    def __init__(self, tables_path: str, out_path: str):
        super().__init__(out_path)
        self.feature_extractor = SqlFeatureExtractor(tables_path)
        self.out_path = out_path

    def process_ast(self, ast: SqlAstNode) -> SqlFeatures:
        features = self.feature_extractor.extract_features(ast)
        features.id = ast.id
        return features
