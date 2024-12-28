import json
import os
import random
from typing import Optional

from pydantic import BaseModel
from openai import OpenAI

from src.augmentation.prompt import GptPromptSubCat, GptPromptCat, GptPrompt
from src.augmentation.text_sql_pair_example import TextSqlPairExample
from src.cat.categorizer import Categorizer
from src.cat.statement_category import StatementCategory
from src.cat.sub_category import SubCategory
from src.cat.tag_extractor import TagExtractor
from src.dbutil.schema_repo import DatabaseSchemaRepo
from src.evaluation.configs import SPIDER_DEV
from src.evaluation.runner.dataset_config import DatasetConfig
from src.sql_parser.parser import SqlParser


class TextSqlPair(BaseModel):
    sql: str
    question: str


class DataGenerator:

    def __init__(self, dataset_config: DatasetConfig):
        self.client = OpenAI(
            organization=os.getenv("OPENAI_GROUP_ID"),
            project=os.getenv("OPENAI_PROJ_ID"),
            timeout=5
        )
        self.schema_repo = DatabaseSchemaRepo(dataset_config.get_tables_path())
        self.examples = extract_examples(self.schema_repo)

    def log(self, message):
        log_file = open("data/aug/gpt.log.json")
        data = json.load(log_file)
        data.append(message)
        log_file = open("data/aug/gpt.log.json", 'w')
        log_file.write(json.dumps(data, indent=4))
        log_file.close()

    def generate_example_for_cat(self, db_id: str, cat: StatementCategory, num_examples: int) -> TextSqlPair:
        if cat in self.examples:
            all_examples = self.examples[cat]
            sample_examples = random.sample(all_examples, min(len(all_examples), num_examples))
        else:
            print(f"No examples exists in the dataset for {cat.name}")
            sample_examples = []

        prompt = GptPromptCat(schema=self.schema_repo.dbs[db_id], cat=cat, examples=sample_examples)
        print(str(prompt))
        result = self.ask(prompt)
        return result

    def generate_example_for_sub_cat(self, db_id: str, cat: SubCategory, num_examples: int) -> Optional[TextSqlPair]:
        if cat in self.examples:
            all_examples = self.examples[cat]
            sample_examples = random.sample(all_examples, min(len(all_examples), num_examples))
        else:
            print(f"No examples exists in the dataset for {cat.name}")
            return None
        prompt = GptPromptSubCat(schema=self.schema_repo.dbs[db_id], cat=cat, examples=sample_examples)
        print(str(prompt))
        result = self.ask(prompt)
        return result

    def ask(self, prompt: GptPrompt):
        try:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                n=1,
                messages=[
                    {
                        "role": "user",
                        "content": str(prompt)
                    }
                ],
                response_format=TextSqlPair
            )
            st = response.model_dump()
            self.log(response.model_dump())
            return response.choices[0].message.parsed
        except Exception as e:
            print(e)


class Catter:
    def __init__(self):
        self.parser = SqlParser()
        self.tag_extractor = TagExtractor()
        self.categorizer = Categorizer()

    def get_category(self, sql: str):
        ast = self.parser.parse(sql)
        tags = self.tag_extractor.extract_tags(ast)
        return self.categorizer.get_category(tags.tag_set)

    def get_sub_category(self, sql: str):
        ast = self.parser.parse(sql)
        tags = self.tag_extractor.extract_tags(ast)
        return self.categorizer.get_sub_category(tags.tag_set)


def extract_examples(schema_repo: DatabaseSchemaRepo):
    catter = Catter()
    examples = {}
    with open(SPIDER_DEV.get_data_path()) as dataset_file:
        dataset_data = json.load(dataset_file)
        for entry in dataset_data:
            db_id = entry["db_id"]
            sql = entry["query"]
            cat = catter.get_sub_category(sql)
            schema = schema_repo.dbs[db_id]
            ex = TextSqlPairExample(sql=sql, question=entry["question"], schema=schema)
            examples.setdefault(cat, []).append(ex)
    return examples
