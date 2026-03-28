import pandas as pd
import tqdm

from src.cat.catter import Catter
from src.util.file_utils import write_json


def categorize(input_file, output_file):
    input_data = pd.read_csv(input_file)
    catter = Catter()
    out_data = []
    for i, row in tqdm.tqdm(input_data.iterrows(), total=len(input_data)):
        sql = row['sql']
        cat = catter.get_category(sql)
        sub = catter.get_sub_category(sql)
        out_data.append({
            'idx': i,
            'dataset': 'sqlshare',
            'query': sql,
            'cat': cat.name,
            'sub': sub.name
        })
    write_json(output_file, out_data)


categorize("data/sqlshare_data_release/cats.csv", "data/sqlshare_data_release/data.json")
