from src.augmentation.data_generator import Catter, TextSqlPair, DataGenerator
from src.augmentation.prompt import get_categories_definition
from src.cat.categories import CATS
from src.cat.sub_category import SubCategory
from src.evaluation.configs import SPIDER_DEV


def evaluate_example(oracle_cat: SubCategory, pair: TextSqlPair):
    catter = Catter()
    cat = catter.get_category(pair.sql)
    print(f"Original Cat: {oracle_cat}, New Cat: {cat}")


def get_sub_cat(name: str):
    for cat in CATS:
        for sub_cat in cat.sub_cats:
            if sub_cat.name == name:
                return sub_cat
    raise RuntimeError(f"No such sub category: {name}")


def main():
    # get_categories_definition()
    generator = DataGenerator(SPIDER_DEV)
    db_id = "concert_singer"
    sub_cat = get_sub_cat("s2")
    print("Generating pair for:")
    print(f"Category: {sub_cat.name}, {sub_cat.description}")
    print(f"DB ID: {db_id}")
    print("##################################################")
    result = generator.generate_example(db_id, sub_cat, 5)
    print("##################################################")
    print(f"Result:\n\t{result}")
    evaluate_example(sub_cat, result)


if __name__ == "__main__":
    main()
