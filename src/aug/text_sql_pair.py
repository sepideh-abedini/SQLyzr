from pydantic import BaseModel


class TextSqlPair(BaseModel):
    sql: str
    question: str
