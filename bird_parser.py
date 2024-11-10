import exact_match

# parser = SqlParser()

path = "data/dataset/bird/"

parser = exact_match.ExactMatchParser("data/dataset/bird/train_tables.json")
scores = 0.0
err = 0.0
line = 0

matched_line_numbers = []

with open(path + "train_gold.sql") as g, open(path + "train_gold.sql") as p:
    gold_lines = g.readlines()
    pred_lines = p.readlines()

    for p, g in zip(pred_lines, gold_lines):
        pred, db_id = p.split("\t")
        g = pred
        db_id = db_id.strip()
        line += 1
        try:
            parsed_pred = parser.parse(pred, db_id)
            parsed_gold = parser.parse(g, db_id)
            if (parsed_pred == parsed_gold) or (parsed_gold == parsed_pred):
                scores += 1.0
                matched_line_numbers.append(line)
            else:
                err += 1.0
                print("*************************** MATCHING ERROR")
                print(f"_______pred_{line} is_________:", pred)
                print(f"_______gold_{line} is_________:", g)
        except Exception as e:
            print("*************************** PARSING ERROR")
            print(f"_______pred_{line} is_________:", pred)
            print(f"_______gold_{line} is_________:", g)
            print(f"______db_id______{line} is_________:", db_id)
            print(e)
            err += 1.0
            # raise e

# with open(path + "s_matched_lines.txt", "w") as out:
#     for line in matched_line_numbers:
#         out.write(str(line) + "\n")
# with open(path+ "all_pred_matched.txt", 'w') as f:
#     for m in pred_matched:
#         f.write(f"{m[0].strip()}\t{m[1].strip()}\n")
#
# with open(path+ "all_gold_matched.txt", 'w') as file:
#         for m in gold_matched:
#             file.write(f"{m}")

print(f"Errors: {err}")
print(f"Matched: {scores}")
print(f"Total: {len(gold_lines)}")
