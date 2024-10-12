import ply.yacc as yacc

# Get the token map from the lexer. This is required.
from .lexer import tokens
from .lexer import get_lexer
from .node import NumNode, BinExprNode


def p_select_statement(p):
    '''expr : NUM
            | expr OP expr'''
    if len(p) == 2:
        p[0] = NumNode(p[1])
    if len(p) == 4:
        p[0] = BinExprNode(p[1], p[2], p[3])


def p_error(p):
    print("Syntax error in input!")
    print(f"Invalid token:{p}")


def get_parser():
    lexer = get_lexer()
    parser = yacc.yacc()
    return parser
