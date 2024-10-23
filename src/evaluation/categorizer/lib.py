from typing import List

CLAUSE_KEYWORDS = ('select', 'from', 'where', 'group', 'order', 'limit', 'intersect', 'union', 'except')
JOIN_KEYWORDS = ('join', 'on', 'as')
AGG_OPS = ('max', 'min', 'count', 'sum', 'avg')
COND_OPS = ('and', 'or')
SQL_OPS = ('intersect', 'union', 'except')
ORDER_OPS = ('desc', 'asc')
CLAUSE_KEYWORDS = ('select', 'from', 'where', 'group', 'order', 'limit', 'intersect', 'union', 'except')

COMPARISON_OPS = ("<","<=",">",">=")
EUQLITY_OPS = ("=","<>")
BOOLEAN_OPS = ("&", "|")
ARITHMETIC_OPS = ("+", "-", "*", "%", "/")
STRING_OPS = ("like", "is")
WHERE_OPS = COMPARISON_OPS + EUQLITY_OPS + BOOLEAN_OPS + ARITHMETIC_OPS + STRING_OPS

SQL_KEYWORDS = CLAUSE_KEYWORDS + JOIN_KEYWORDS + AGG_OPS + COND_OPS + SQL_OPS + ORDER_OPS + CLAUSE_KEYWORDS + WHERE_OPS

Tokens = List[str]

def tokenize(sql: str) -> Tokens:
    return sql.split(" ")

def get_db_id(tokens: Tokens) -> str:
    from_idx = tokens.index("from")
    return tokens[from_idx+1]
    

def remove_all_nested_queries(tokens: Tokens) -> Tokens:
    assert tokens[0] == "select"
    while "select" in tokens[1:]:
        tokens = remove_nested_queries(tokens)
    return tokens

def find_next_clause_idx(tokens: Tokens) -> int:
    for index, word in enumerate(tokens):
        if word in CLAUSE_KEYWORDS:
            return index
    return -1

def get_where_clause_operators(tokens: Tokens) -> Tokens:
    operators = []
    for word in tokens:
        if word in WHERE_OPS:
            operators.append(word)
    return operators

def get_where_clause(tokens: Tokens):
    where_start_idx = tokens.index("where")
    next_clause_idx = find_next_clause_idx(tokens[where_start_idx+1:])
    
    if next_clause_idx == -1:
        where_end_idx = len(tokens) - 1
    else:
        where_end_idx = where_start_idx + next_clause_idx
    return tokens[where_start_idx:where_end_idx+1]

def find_matching_par(tokens: Tokens, par_idx: int) -> int:
    stack = ["("]
    i = par_idx + 1
    while len(stack) > 0:
        if tokens[i] == "(":
            stack.append("(")
        if tokens[i] == ")":
            stack.pop()
        i += 1
    return i - 1

def extract_nested_statements(tokens: Tokens) -> Tokens:
    # assert tokens[0].word == "select", "Expected select as the first token: {}".format(tokens)
    if not "select" in tokens[1:]:
        return tokens, []
    select_idx = tokens[1:].index("select") + 1
    nested_query_start_idx = select_idx - 1
    assert tokens[nested_query_start_idx] == '(', "Expected '(' before nested 'select', {}".format(tokens[nested_query_start_idx-1:nested_query_start_idx+2])
    nested_query_end_idx = find_matching_par(tokens, nested_query_start_idx)
    return tokens[0: nested_query_start_idx] + tokens[nested_query_end_idx+1:], tokens[nested_query_start_idx+1:nested_query_end_idx]

def extract_sub_statements(tokens: Tokens) -> Tokens:
    sub_statements = []
    separators = []
    idx = 0
    begin = idx
    while idx < len(tokens):
        token = tokens[idx]
        if idx > 0 and token == 'select' and tokens[idx-1] == "(":
            nested_query_end_idx = find_matching_par(tokens, idx)
            idx = nested_query_end_idx
        if token in SQL_OPS:
            sub_statements.append(tokens[begin: idx])
            begin = idx + 1
            separators.append(token)
        idx += 1
    sub_statements.append(tokens[begin: ])
    return sub_statements, separators
            
    