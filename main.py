import argparse

from config import CONFIG
from src.batch.category_exporter import BatchCategoryExporter
from src.batch.diagram_exporter import BatchAstDiagramExporter
from src.batch.spider_pre_processor import SpiderPreProcessor
from src.batch.batch_sql_parser import BatchSqlParser
from src.batch.batch_feature_extractor import BatchFeatureExporter
from src.batch.tag_plot_processor import TagPlotProcessor
from src.batch.tag_exporter import BatchTagExporter

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--samples", type=int)
parser.add_argument("-f", "--features", action='store_true')
parser.add_argument("-c", "--cats", action='store_true')
parser.add_argument("-g", "--graph", action='store_true')
parser.add_argument("-t", "--tags", action='store_true')
args = parser.parse_args()


def main():
    pre_processor = SpiderPreProcessor(in_path=CONFIG.dev_path(), out_path=CONFIG.sql_path())
    pre_processor.process()

    sql_processor = BatchSqlParser(in_path=CONFIG.sql_path())
    asts = sql_processor.process()

    if args.samples:
        asts = asts[:args.samples]

    if args.features:
        feature_extractor = BatchFeatureExporter(tables_path=CONFIG.tables_path(), out_path=CONFIG.features_path())
        feature_extractor.process(asts)

    if args.graph:
        graph_processor = BatchAstDiagramExporter(diagram_out_path_tpl=CONFIG.graph_path_tpl(),
                                                  out_path=CONFIG.graphs_path())
        graph_processor.process(asts)

    if args.cats:
        cat_processor = BatchCategoryExporter(out_path=CONFIG.cats_path())
        cat_processor.process(asts)

    if args.tags:
        tag_processor = BatchTagExporter(out_path=CONFIG.tags_path())
        tag_processor.process(asts)
        tag_plotter = TagPlotProcessor(in_path=CONFIG.tags_path())
        tag_plotter.process()


if __name__ == '__main__':
    main()
