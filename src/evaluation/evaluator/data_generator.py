import pandas as pd

from src.cat.categorizer import Categorizer
from src.cat.tag_extractor import TagExtractor
from src.sql_parser.parser import SqlParser


def generate_evaluation_data(pred_path: str, gold_path: str, eval_data_path: str, samples_per_cat: int):
    parser = SqlParser()
    tag_extractor = TagExtractor()
    categorizer = Categorizer()
    cat_counts = {}

    with open(pred_path) as pred_file, open(gold_path) as gold_file:
        pred_file_lines = pred_file.readlines()
        rows = []
        for i, gold_line in enumerate(gold_file):
            gold_sql, db_id = gold_line.strip().split("\t")
            ast = parser.parse(gold_sql)
            tags = tag_extractor.extract_tags(ast)
            cat = categorizer.get_category(tags.tag_set)
            pred_sql = pred_file_lines[i].strip()
            row = {'idx': i, 'gold': gold_sql, 'pred': pred_sql, 'db_id': db_id, 'cat': cat}
            rows.append(row)
            # if cat in cat_counts:
            #     if cat_counts[cat] < samples_per_cat:
            #         rows.append(row)
            #     cat_counts[cat] = cat_counts[cat] + 1
            # else:
            #     rows.append(row)
            #     cat_counts[cat] = 1
    df = pd.DataFrame(rows)
    df.to_json(eval_data_path)
    df.to_csv(eval_data_path + ".csv")
