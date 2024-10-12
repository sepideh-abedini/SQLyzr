from src.batch.exporter import BatchAstExporterProcessor, T
from src.cat.statement_tag import StatementTag
from src.cat.tag_extractor import TagExtractor
from src.sql_parser.node import SqlAstNode
from src.util.meta_utils import get_all_subclasses


class BatchTagExporter(BatchAstExporterProcessor):
    """Input: List[SqlAstNode]
       Output: One column for each tag type
    """

    def __init__(self, out_path: str):
        super().__init__(out_path)
        self.tag_extractor = TagExtractor()

    def process_ast(self, ast: SqlAstNode) -> T:
        tag_types = get_all_subclasses(StatementTag)
        tag_set = self.tag_extractor.extract_tags(ast)
        tag_set = tag_set.tag_set.reduce()
        row = {}
        for tt in tag_types:
            row[tt.__name__] = tag_set.get_val(tt)
        return row
