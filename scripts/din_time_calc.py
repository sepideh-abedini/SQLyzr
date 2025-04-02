import sys
from datetime import datetime
from pathlib import Path

from src.configs.config_loader import load_config
from src.gpt.gateway.batch.batch_client import GptBatchClient

conf_path = sys.argv[1]
conf = load_config(conf_path)

prefix = "data/dail_spider_all/pred/pred_0.2_0.txt"
suffs = ["train.schema.jsonl", "test.schema.jsonl", "questions.json", "sql.in.jsonl", "sql.out.jsonl",
         "second.questions.json", "sql.in.second.jsonl", "sql.out.second.jsonl", ""]


def print_path_times(p: Path):
    print(p)
    ft = datetime.fromtimestamp(p.stat().st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    print("ATIME: ", ft)
    ft = datetime.fromtimestamp(p.stat().st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    print("CTIME: ", ft)
    ft = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    print("MTIME: ", ft)
    print("#######################")

for suff in suffs:
    print_path_times(Path(f"{prefix}.{suff}"))
# prefix = "data/dail_spider_all/pred/pred_0.2_0.txt"

# with open(bid_file) as file:
#     bid = file.read()
#
# client = GptBatchClient()
# batch = client.retrieve_batch(bid)
# print(batch.completed_at-batch.created_at)
# print(batch.completed_at)
