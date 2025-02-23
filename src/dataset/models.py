from pydantic import BaseModel


class SpiderExample(BaseModel):
    db_id: str
    query: str
    question: str
    idx: int = 0
