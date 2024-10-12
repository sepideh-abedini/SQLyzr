import re

from src.sql_parser.node import SelectStatementNode
from src.sql_parser.parser import SqlParser


def parse(sql) -> SelectStatementNode:
    parser = SqlParser()
    ast = parser.parse(sql)
    return ast


def erase_surrounding_ws(s: str, c) -> str:
    return re.sub(f'\s*\{c}\s*', c, s)


def shrink_whitespaces(s: str) -> str:
    # s = re.sub(r'\s*\(\s*', '(', s)
    s = erase_surrounding_ws(s, ',')
    s = erase_surrounding_ws(s, '(')
    s = erase_surrounding_ws(s, ')')
    return re.sub(r'\s+', ' ', s)


def erase_char(s: str, i: int):
    return s[:i] + ' ' + s[i + 1:]


def erase_outer_pars(s: str) -> str:
    if s[0] == '(' and s[len(s) - 1] == ')':
        s = s[1:len(s) - 1]
    return s


def clean_sql_str(s: str) -> str:
    s = s.strip()
    s = erase_outer_pars(s)
    s = shrink_whitespaces(s)
    s = erase_consecutive_pars(s)
    s = shrink_whitespaces(s)
    s = s.strip()
    s = s.lower()
    return s


def assert_sql_str_equal(s1: str, s2: str) -> bool:
    s1 = clean_sql_str(s1)
    s2 = clean_sql_str(s2)
    assert s1 == s2


def find_kth_left_par(s: str, k: int):
    lefts = []
    for i, c in enumerate(s):
        if c == '(':
            lefts.append(c)
            if len(lefts) == k:
                return i


def find_right_par(s: str, left_par_idx: int):
    stack = []
    for i, c in enumerate(s):
        if i > left_par_idx:
            if c == '(':
                stack.append('(')
            elif c == ')':
                if len(stack) == 0:
                    return i
                else:
                    stack.pop()


def erase_consecutive_pars(s: str) -> str:
    for i in range(len(s) - 1):
        if s[i] == s[i + 1] == '(':
            j = i + 1
            while j < len(s) - 1:
                if s[j] == s[j + 1] == ')':
                    s = erase_char(s, i)
                    s = erase_char(s, j)
                    return s
                j += 1
    return s
