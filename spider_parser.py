from fontTools.misc.psOperators import ps_real

from src.sql_parser.parser import SqlParser
from utils import parse
import exact_match

# parser = SqlParser()

path = "data/datasets/spider/"

parser = exact_match.ExactMatchParser()
scores = 0.0
err = 0.0
line = 0

matched_line_numbers = []

with open(path + "pred_example.txt") as g, open(path + "gold_example.txt") as p:
    gold_lines = g.readlines()
    pred_lines = p.readlines()

    for p, g in zip(pred_lines, gold_lines):
        pred, db_id = p.split("\t")
        db_id = db_id.strip()
        # print("________pred is_________:", pred)
        # print("________gold is_________:", g)
        # print("________db is_________:", db_id)
        line += 1
        # print(f"PROCESSING: {line}")
        try:
            parsed_pred = parser.parse(pred, db_id)
            parsed_gold = parser.parse(g, db_id)
        except Exception as e:
            print("*************************** PARSING ERROR")
            print(f"_______pred_{line} is_________:", pred)
            print(f"_______gold_{line} is_________:", g)
            print(f"______db_id______{line} is_________:", db_id)
            print(e)
            # raise e
        if (parsed_pred == parsed_gold ) or (parsed_gold == parsed_pred):
            scores += 1.0
            matched_line_numbers.append(line)
        else:
            # print(f"_______pred_{line} is_________:",pred)
            # print(f"_______gold_{line} is_________:",g)
            # print(f"______db_id______{line} is_________:", db_id)
            err += 1.0

with open(path + "s_matched_lines.txt", "w") as out:
    for line in matched_line_numbers:
        out.write(str(line) + "\n")
# with open(path+ "all_pred_matched.txt", 'w') as f:
#     for m in pred_matched:
#         f.write(f"{m[0].strip()}\t{m[1].strip()}\n")
#
# with open(path+ "all_gold_matched.txt", 'w') as file:
#         for m in gold_matched:
#             file.write(f"{m}")

length = len(g)
exact_score = scores / length
print(scores)




