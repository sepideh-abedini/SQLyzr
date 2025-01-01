from src.sqlyzr_conf import DIN_SPIDER_SMALL
from src.third_party.dail.data_preprocess import preprocess_data
from src.third_party.dail.generate_question import generate_questions


def main():
    conf = DIN_SPIDER_SMALL.eval_conf
    preprocess_data(
        input_path=conf.dataset_config.get_data_path(),
        output_path="data/dail/schema_links.jsonl",
        db_path=conf.dataset_config.get_db_path(),
        tables_path=conf.dataset_config.get_tables_path()
    )

    generate_questions(
        tables_path=conf.dataset_config.get_tables_path(),
        output_path=conf.questions_path,
        db_dir=self.config.dataset_config.get_db_path(),
        input_path=self.config.dataset_config.get_data_path(),
        schema_links_path=self.schema_links_path
    )
    print("Question generation done")
    print("Hello")


if __name__ == '__main__':
    main()
