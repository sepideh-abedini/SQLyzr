from src.cat.categorizer import Categorizer
from src.cat.tag_extractor import TagExtractor
from src.batch.exporter import BatchAstExporterProcessor, T
from src.sql_parser.node import SqlAstNode


class BatchCategoryExporter(BatchAstExporterProcessor):
    """Input: List[SqlAstNode]
       Output: CSV['id', 'sql', 'cat', 'question']
    """

    def __init__(self, out_path: str):
        super().__init__(out_path)
        self.tag_extractor = TagExtractor()
        self.categorizer = Categorizer()

    def process_ast(self, ast: SqlAstNode) -> T:
        tags = self.tag_extractor.extract_tags(ast)
        cat = self.categorizer.get_category(tags.tag_set)
        return {
            'id': ast.id,
            'db_id': ast.db_id,
            'sql': ast.raw_sql,
            'question': ast.question,
            'cat': cat
        }
