from pydantic import BaseModel


class TextSqlPair(BaseModel):
    sql: str
    question: str

class GeneratedTextSqlPair(BaseModel):
    sql: str
    question: str
    sub_cat: str
    db_id: str
