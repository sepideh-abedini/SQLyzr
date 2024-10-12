from src.batch.spider_pre_processor import SpiderPreProcessor
from src.batch.batch_sql_parser import BatchSqlParser
from src.batch.category_exporter import BatchCategoryExporter
from src.batch.spider_sampler import SpiderSampler

import pandas as pd
preprocessor = SpiderPreProcessor("data/datasets/spider/dev.json", "out/spider.csv" )
preprocessor.process()

parser = BatchSqlParser("out/spider.csv")
ASTlist = parser.process()

categorizer = BatchCategoryExporter("out/spider_categories.csv")
df = categorizer.process(ASTlist)

sampler = SpiderSampler("out/spider_categories.csv","out/spider_sample.json")
sampler.process()







