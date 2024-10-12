from src.batch.exporter import BatchAstExporterProcessor, T
from src.prop_collectors.graph_drawer import draw_graph
from src.sql_parser.node import SqlAstNode


class BatchAstDiagramExporter(BatchAstExporterProcessor):
    """Input: List[SqlAstNode]
       Processing: exports AST diagram of each statement as a separate file
       Output: CSV[id, path]
               path: diagram file
    """

    def __init__(self, diagram_out_path_tpl: str, out_path: str):
        super().__init__(out_path)
        self.diagram_out_path_tpl = diagram_out_path_tpl

    def process_ast(self, ast: SqlAstNode) -> T:
        out_path = self.diagram_out_path_tpl.format(ast.id)
        draw_graph(ast, out_path)
        return {'id': ast.id, 'path': out_path}
