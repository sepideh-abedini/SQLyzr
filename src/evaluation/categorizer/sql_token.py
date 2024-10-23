from enum import Enum
import re

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

class SqlDataType(Enum):
    String = 1
    Number = 2
    Date = 3

def is_wrapped_in_single_quotes(s: str) -> bool:
    pattern = r"^'.*'$"
    return bool(re.match(pattern, s))


def is_value(word: str) -> bool:
    return is_wrapped_in_single_quotes(word) or word.isnumeric()

class SqlToken:
    def __init__(self, word: str) -> None:
        self.word = word
    
    def __repr__(self) -> str:
        # return "{}:{}".format(self.__class__.__name__, self.word)
        return str(self)

    def __str__(self) -> str:
        return "{}".format(self.word)
    
    def __eq__(self, __value: object) -> bool:
        if type(__value) == str:
            return __value == self.word
        return False

class ValueToken(SqlToken):
    def __init__(self, word: str) -> None:
        super().__init__(word)

class IdentifierToken(SqlToken):
    def __init__(self, word: str) -> None:
        super().__init__(word)

class KeywordToken(SqlToken):
    def __init__(self, word: str) -> None:
        super().__init__(word)

class SubQueryToken(SqlToken):
    def __init__(self, word: str) -> None:
        super().__init__(word)

class TokenFactory:
    def __init__(self) -> None:
        pass

    @staticmethod
    def create_token(word: str) -> SqlToken:
        if word in SQL_KEYWORDS:
            return KeywordToken(word)
        elif is_value(word):
            return ValueToken(word)
        else:
            return IdentifierToken(word)
