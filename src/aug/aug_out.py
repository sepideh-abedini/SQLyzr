from src.aug.text_sql_pair import TextSqlPair


class AugOut(TextSqlPair):
    sql: str
    question: str
    db_id: str
    sub_cat: str
