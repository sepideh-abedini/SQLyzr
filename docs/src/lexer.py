import re

import ply.lex as lex

tokens = [
    'NUM',
    'OP',
]

t_OP = r'[-+]'


def t_NUM(t):
    r'(\d+)'
    t.value = int(t.value)
    return t


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    # print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def get_lexer():
    lexer = lex.lex(reflags=re.IGNORECASE)
    return lexer
