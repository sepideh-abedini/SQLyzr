from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from src.augmentation.text_sql_pair_example import TextSqlPairExample
from src.cat.categories import CATS
from src.cat.statement_category import StatementCategory
from src.cat.sub_category import SubCategory
from src.dbutil.database_schema import DatabaseSchema

PROMPT_TEMPLATE = """
You are a SQLite SQL expert. Your job is to create an example consists of a natural language question 
and a SQL query to fetch the data for it regarding the given schema that satisfies the given constraints. 

Constraints are defined as follows:
{category_definitions}

The SQL query should be generated for a database with the following schema:
{schema_str}

The SQL query should satisfy at least on of the following constraints:
{sub_cats}

The SQL query should not satisfy any of the following constraints:
{exclude_sub_cats}

I will show you multiple examples generated for the other database and its table schemas.
Examples:

{examples_str}
"""


def get_categories_definition():
    res = "Constraints:\n"
    for cat in CATS:
        for sub in cat.sub_cats:
            res += f"\t{sub.name}: {sub.description}\n"
    return res


def get_non_matching_sub_cats(sub_cat: SubCategory):
    sub_cats = set()
    start = False
    for cat in CATS:
        if sub_cat in cat.sub_cats:
            start = True
        if start:
            sub_cats.update(cat.sub_cats)
    sub_cats.discard(sub_cat)
    return sub_cats


def get_non_matching_sub_cats_of_cat(cat: StatementCategory):
    sub_cats = set()
    start = False
    for c in CATS:
        if start:
            sub_cats.update(c.sub_cats)
        if cat == c:
            start = True
    return sub_cats


class GptPrompt(ABC):
    @abstractmethod
    def __str__(self):
        pass


@dataclass
class GptPromptCat(GptPrompt):
    cat: StatementCategory
    schema: DatabaseSchema
    examples: List[TextSqlPairExample]

    def __str__(self):
        examples_str = "\n".join([f"Example Number {i + 1}:\n{str(e)}" for i, e in enumerate(self.examples)])
        return PROMPT_TEMPLATE.format(
            examples_str=examples_str,
            schema_str=str(self.schema),
            category_definitions=get_categories_definition(),
            sub_cats=",".join([s.name for s in self.cat.sub_cats]),
            exclude_sub_cats=",".join([s.name for s in get_non_matching_sub_cats_of_cat(self.cat)])
        )


@dataclass
class GptPromptSubCat(GptPrompt):
    cat: SubCategory
    schema: DatabaseSchema
    examples: List[TextSqlPairExample]

    def __str__(self):
        examples_str = "\n".join([str(e) for e in self.examples])
        return PROMPT_TEMPLATE.format(
            examples_str=examples_str,
            schema_str=str(self.schema),
            category_definitions=get_categories_definition(),
            sub_cats=self.cat.name,
            exclude_sub_cats=",".join([s.name for s in get_non_matching_sub_cats(self.cat)])
        )
