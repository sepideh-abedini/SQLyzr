import json
import random

from src.aug.calculate_cost import calculate_cost
from src.aug.data_generator import Catter, TextSqlPair, DataGenerator
from src.cat.categories import CAT_4
from src.cat.statement_category import StatementCategory
from src.cat.sub_category import SubCategory
from src.eval.configs import SPIDER_DEV, DIN_SMALL_CONF


def trunc_logs():
    data = []
    file = open("data/aug/gpt.log.json", "w")
    file.write(json.dumps(data))
    file.close()


def evaluate_example(oracle_cat: SubCategory, pair: TextSqlPair):
    catter = Catter()
    cat = catter.get_category(pair.sql)
    print(f"Original Cat: {oracle_cat}, New Cat: {cat}")


def generate_example_for_sub_cat(sub_cat, db_id) -> TextSqlPair:
    generator = DataGenerator(DIN_SMALL_CONF.dataset_config)
    print("##################################################")
    result = generator.generate_example_for_sub_cat(db_id, sub_cat, 10)
    print("##################################################")
    print("Generated pair for:")
    print(f"Category: {sub_cat.name}, {sub_cat.description}")
    print(f"DB ID: {db_id}")
    print(f"Result:\n\t{result}")
    # evaluate_example(sub_cat, result)
    return result
    # result = generator.generate_example_for_sub_cat(db_id, sub_cat, 5)


def generate_examples(cat: StatementCategory, db_id: str):
    results = []
    wrong_results = []
    catter = Catter()
    num = 5

    trunc_logs()

    generator = DataGenerator(SPIDER_DEV)
    sub_cats = []
    for s in cat.sub_cats:
        if s in generator.examples.keys():
            sub_cats.append(s)
    print(f"Generating for sub_cats: {sub_cats}")

    for i in range(num):
        sub_cat = random.choice(list(sub_cats))
        result = generate_example_for_sub_cat(sub_cat, db_id)
        if result is None:
            continue
        try:
            new_cat = catter.get_category(result.sql)
            new_sub_cat = catter.get_sub_category(result.sql)
        except Exception as e:
            print(e)
            continue
        data = {
            "db_id": db_id,
            "cat": cat.name,
            "sub_cat": sub_cat.name,
            "new_cat": new_cat.name,
            "new_sub_cat": new_sub_cat.name,
            "query": result.sql,
            "question": result.question
        }
        if new_cat == cat:
            results.append(data)
        else:
            wrong_results.append(data)

    out_file = open("data/aug/gpt.json", "w")
    out_file.write(json.dumps(results, indent=4))

    out_file = open("data/aug/gpt.wrong.json", "w")
    out_file.write(json.dumps(wrong_results, indent=4))

    print("****************************************************************************")

    calculate_cost()
    print(f"Requested num: {num}")
    print(f"Correct results: {len(results)}")
    print(f"Wrong results: {len(wrong_results)}")

    # sql = "SELECT name, song_name FROM singer INTERSECT SELECT name, song_name FROM singer WHERE age > (SELECT AVG(age) FROM singer) ORDER BY name;"
    # catter = Catter()
    # print(catter.get_category(sql))
    # generate_example_for_sub_cat(cat, db_id)
