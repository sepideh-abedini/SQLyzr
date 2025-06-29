import json
import re

gold_file = "data/bird/data.test.small.bad.json"
pred_file = "out/simple_bird_bad_msc/output_stage3.json"
output_file = "out/simple_bird_bad_msc/pred/simple/bird/pred_0.2_0.txt"

with open(gold_file, "r") as f:
    gold_data = json.load(f)

with open(pred_file, "r") as f:
    pred_data = json.load(f)

with open(output_file, "w") as f:
    for pred in pred_data:
        psql = pred["sql_pred"].strip().replace("\n", " ")
        match = re.search(r"/([^/]+)/[^/]+\.sqlite$", pred['db_path'])
        db_id = match.group(1)
        f.write(f"{psql}\t{db_id}\n")

with open("pred_dbids.txt", "w") as f:
    for pred in pred_data:
        match = re.search(r"/([^/]+)/[^/]+\.sqlite$", pred['db_path'])
        db_id = match.group(1)
        f.write(f"{db_id}\n")

with open("gold_dbids.txt", "w") as f:
    for gold in gold_data:
        db_id = gold["db_id"]
        f.write(f"{db_id}\n")
exit(0)
# pred_lookup = {}
# for obj in pred_data:
#     match = re.search(r"\d+", obj["idx"])
#     if match:
#         pred_lookup[int(match.group())] = obj["sql_pred"]

i = 0
j = 0
with open(output_file, "w") as f:
    while i < len(gold_data):
        gold = gold_data[i]
        pred = pred_data[j]
        gsql = gold["query"].strip()
        psql = pred["sql_pred"].strip().replace("\n", " ")
        match = re.search(r"/([^/]+)/[^/]+\.sqlite$", pred['db_path'])
        if match:
            db_id = match.group(1)
        print(f"Gold[{i}] - {gold['db_id']}:", gsql)
        print(f"Pred[{j}] - {db_id}:", psql)
        match = input("Match? (y/n):")
        if match == "y":
            j += 1
        else:
            psql = "SELECT"
        f.write(psql + "\n")
        i += 1

# with open(output_file, "w") as f:
#     for gold in gold_data:
#         qid = gold["question_id"]
#         if qid not in pred_lookup:
#             sql = gold["sql"]
#         else:
#             sql = "SELECT"
#         f.write(sql + "\n")
