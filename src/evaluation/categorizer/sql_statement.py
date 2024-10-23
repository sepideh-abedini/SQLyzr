from typing import List
from sql_token import SqlToken, SqlDataType,KeywordToken
from lib import extract_nested_statements, extract_sub_statements
from schema_tools import TableMetadata

def get_nest_level(tokens: List[SqlToken]) -> int:
    nest_level = 0
    _, tokens = extract_nested_statements(tokens)
    while tokens:
        nest_level += 1
        _, tokens = extract_nested_statements(tokens)
    return nest_level

def get_db_id(tokens: List[SqlToken]) -> str:
    for idx, token in enumerate(tokens):
        if token == 'from':
            assert idx < len(tokens) - 1, "Expected db name after from"
            return tokens[idx + 1]
    raise("Couldn't find database id: {}".format(tokens))

def process_aliases(tokens: List[SqlToken]):
    for idx, token in enumerate(tokens):
        if isinstance(token, KeywordToken) and token == "as":
            db_id = tokens[idx - 1]
            alias = tokens[idx + 1]

class SqlStatement:
    def __init__(self, tokens: List[SqlToken]) -> None:
        sub_statements, separators = extract_sub_statements(tokens)
        self.sub_statements = []
        if len(sub_statements) > 1: 
            self.sub_statements = [SqlStatement(s) for s in sub_statements]
            tokens = separators
        
        self.nested_statements = []
        tokens, nested_tokens = extract_nested_statements(tokens)
        
        self.tokens = tokens
        if nested_tokens:
            self.nested_statements.append(SqlStatement(nested_tokens))
        self.db_id = get_db_id(self.tokens)
        self.data_types = []
        print(process_aliases(self.tokens))
    
    def get_nest_level(self):
        if len(self.sub_statements) == 0:
            if len(self.nested_statements) == 0:
                return 0
            else:
                return self.nested_statements[0].get_nest_level() + 1
        else:
            max = -1
            for s in self.sub_statements:
                level = s.get_nest_level()
                if level > max:
                    max = level
        return max

    def __repr__(self) -> str:
        return str(self.tokens)
    
    def get_sql(self) -> str:
        return " ".join([token.word for token in self.tokens])

    