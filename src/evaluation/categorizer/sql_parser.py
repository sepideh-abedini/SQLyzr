from typing import List
from sql_token import SqlToken, TokenFactory
from sql_statement import SqlStatement
from lib import extract_sub_statements
import re

Tokens = List[str]


def clean_sql(sql):
    # Delete double quotes
    # Delete extra parantheses
    sql = re.sub(r'(\))', r'\1 ', sql)
    sql = re.sub(r'(\()', r' \1', sql)
    return sql
    
class SqlParser:
    def __init__(self) -> None:
        pass

    def to_statement(self, sql_str: str) -> Tokens:
        sql_str = clean_sql(sql_str)
        words = re.split(r'\s+', sql_str)
        words = [w.strip() for w in words]
        words = [w.lower() for w in words]
        tokens = [TokenFactory.create_token(w) for w in words]
        statement = SqlStatement(tokens)
        return statement
        