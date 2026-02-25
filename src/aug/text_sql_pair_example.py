from dataclasses import dataclass

from src.util.database_schema import DatabaseSchema

EXAMPLE_STR_FORMAT = """
********** Example **********
{schema}
SQL: {sql}
Question: {question}
*****************************
"""


@dataclass
class TextSqlPairExample:
    sql: str
    question: str
    schema: DatabaseSchema

    def __str__(self):
        return EXAMPLE_STR_FORMAT.format(
            sql=self.sql,
            question=self.question,
            schema=str(self.schema)
        )
