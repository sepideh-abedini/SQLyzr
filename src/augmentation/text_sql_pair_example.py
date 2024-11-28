from dataclasses import dataclass

from src.dbutil.database_schema import DatabaseSchema

EXAMPLE_STR_FORMAT = """
**********
SQL: {sql}
Question: {question}
Schema: 
\t{schema}
**********
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
