import re
from datetime import datetime

import ply.lex as lex

fun_names = {
    'avg': 'AVG',
    'sum': 'SUM',
    'min': 'MIN',
    'max': 'MAX',
    'count': 'COUNT'
}

sort_orders = {
    'asc': 'ASC',
    'desc': 'DESC'
}

set_ops = {
    'union': 'UNION',
    'except': 'EXCEPT',
    'intersect': 'INTERSECT'
}

logic_ops = {
    'and': 'AND',
    'or': 'OR'
}

keywords = {
    'select': 'SELECT',
    'from': 'FROM',
    'where': 'WHERE',
    'group': 'GROUP',
    'join': 'JOIN',
    'order': 'ORDER',
    'limit': 'LIMIT',
    'like': 'LIKE',
    'having': 'HAVING',
    'on': 'ON',
    'by': 'BY',
    'as': 'AS',
    'in': 'IN',
    'is': 'IS',
    'null': 'NULL',
    'not': 'NOT',
    'between': 'BETWEEN',
    'distinct': 'DISTINCT',
    'exists': 'EXISTS',
    'inner': 'INNER',
    'cast': 'CAST',
    'integer': 'INTEGER',
    'float': 'FLOAT',
    'real': 'REAL',
    'left': 'LEFT',
    'rank': 'RANK',
    'dense_rank': 'DENSE_RANK',
    'partition': 'PARTITION',
    'over': 'OVER',
    'end': 'END',
    'then': 'THEN',
    'else': 'ELSE',
    'case': 'CASE',
    'when': 'WHEN',
    'with' : 'WITH',
    'recursive' : 'RECURSIVE',
    'int' : 'INT'
}

reserved = keywords | sort_orders | set_ops | logic_ops

tokens = [
             'COMMA',
             'LPAREN',
             'RPAREN',
             'COMP_OP',
             'ARITH_OP',
             'DATE',
             'NUMBER',
             'DOT',
             'STRING',
             'STAR',
             'ID',
             'ORR'
         ] + list(reserved.values())

t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_STAR = r'\*'
t_DOT = r'\.'
t_ORR = r'\|\|'


def t_DATE(t):
    r'\d{4}-\d{2}-\d{2}'  # Match dates in YYYY-MM-DD format
    return t


def t_NUMBER(t):
    r'(\d+\.\d+)|(\-\d+)|(\d+)'
    if t.value.isdigit():
        t.value = int(t.value)
    else:
        t.value = float(t.value)
    return t


# r'\'[^\']*\'|\"[^\"]*\"'
def t_STRING(t):
    r"\'([^']|'')*\'|\"([^\"]|\"\")*\""
    val = str(t.value)
    val = val.replace("\"", "")
    val = val.replace("\'", "")
    val = val.replace("\''", "")
    t.value = val
    return t


def t_ARITH_OP(t):
    r'[-+/]'
    return t


# FIXME: handle != op
def t_COMP_OP(t):
    r'!=|<>|>=|<=|=|>|<'
    return t


def t_ID(t):
    r'\w+'
    t.value = t.value.lower()
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


# A string containing ignored characters (spaces and tabs)
t_ignore = ' '


# Error handling rule
def t_error(t):
    # print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def get_lexer():
    lexer = lex.lex(reflags=re.IGNORECASE)
    return lexer
