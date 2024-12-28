from src.evaluation.evaluator.exact_match import ExactMatchParser
from src.exprimental.matcher.sql_transformer import *
from src.exprimental.transformer_detector import TransformerDetector


def main():
    idx = 12
    nl = "List all song names by singers above the average age."
    db_id = "concert_singer"
    pred = "SELECT Song_Name, Age FROM singer WHERE Age > (SELECT AVG(Age) FROM singer) ORDER BY Song_Name"
    gold = "SELECT song_name, Age FROM singer WHERE age  >  (SELECT avg(age) FROM singer)"

    pred = SqlInputData(db_id, pred)
    gold = SqlInputData(db_id, gold)

    detector = TransformerDetector()
    sub = detector.find_working_sub(pred, gold)

    print(sub)


if __name__ == "__main__":
    pred = "SELECT COUNT(*) FROM singer"
    gold = "SELECT count(*) FROM singer"
    db_id = "concert_singer"
    parser = ExactMatchParser("data/spider/tables.json")
    pred = parser.parse(pred, db_id)
    gold = parser.parse(gold, db_id)
    print(pred == gold)
    # main()

# for s in x:
#     print(s)


# print(x)
