import ply.yacc as yacc
from numpy.lib.recfunctions import join_by

# Get the token map from the lexer. This is required.
from .lexer import tokens, logic_ops
from .lexer import get_lexer
from .node import *


precedence = (
    ('left', 'OR', 'AND'),
    ('left', 'COMP_OP', 'ARITH_OP')
)

def p_select_statement(p):
    '''select_statement : select_core
                        | select_statement set_op select_core
                        | select_statement order_by
                        | select_statement limit'''
    if len(p) == 2:
        p[0] = SelectStatementNode([p[1]], [])
    else:
        if len(p) == 4:
            p[0] = p[1].add_core(p[2], p[3])
        elif isinstance(p[2], OrderByNode):
            p[0] = replace(p[1], orderby=p[2])
        elif isinstance(p[2], LimitNode):
            p[0] = replace(p[1], limit=p[2])


def p_select_core(p):
    '''select_core : select_clause from_clause
                   | select_core where_clause
                   | select_core group_clause'''
    if isinstance(p[1], SelectClauseNode):
        p[0] = SelectCoreNode(p[1], p[2])
    if isinstance(p[1], SelectCoreNode):
        if isinstance(p[2], WhereClauseNode):
            p[0] = replace(p[1], where_clause=p[2])
        elif isinstance(p[2], GroupClauseNode):
            p[0] = replace(p[1], group_clause=p[2])


def p_select_clause(p):
    '''select_clause : SELECT result_column
                     | SELECT DISTINCT result_column
                     | select_clause COMMA result_column'''
    if len(p) == 3:
        p[0] = SelectClauseNode([p[2]])
    else:
        if isinstance(p[1], SelectClauseNode):
            p[0] = p[1] + p[3]
        else:
            p[0] = SelectClauseNode([p[3]], True)


def p_result_column(p):
    '''result_column : expr
                     | expr AS column_alias'''
    if len(p) == 2:
        p[0] = ResultColumnNode(p[1])
    else:
        p[0] = ResultColumnNode(p[1], p[3])


def p_order_by(p):
    '''order_by : ORDER BY ordering_term
                | order_by COMMA ordering_term'''
    if isinstance(p[1], OrderByNode):
        p[0] = p[1] + p[3]
    else:
        p[0] = OrderByNode([p[3]])


def p_ordering_term(p):
    '''ordering_term : expr
                     | expr sort_order'''
    if len(p) == 2:
        p[0] = OrderingTerm(p[1])
    else:
        p[0] = OrderingTerm(p[1], p[2])


def p_limit(p):
    '''limit : LIMIT expr'''
    p[0] = LimitNode(p[2])


def p_from_clause(p):
    '''from_clause : FROM table_or_subquery
                   | from_clause COMMA table_or_subquery
                   | FROM join_clause'''

    if len(p) == 3:
        if isinstance(p[2], TableOrSubqueryNode):
            p[0] = FromClauseNode([p[2]])
        else:
            p[0] = FromClauseNode([], p[2])
    else:
        p[0] = p[1] + p[3]


def p_table_or_subquery(p):
    '''table_or_subquery : table_name
                         | table_name AS table_alias
                         | LPAREN select_statement RPAREN
                         | LPAREN select_statement RPAREN table_alias
                         | LPAREN select_statement RPAREN AS table_alias'''
    if len(p) == 2:
        p[0] = TableOrSubqueryNode(table_name=p[1])
    elif len(p) == 4:
        if isinstance(p[2], SelectStatementNode):
            p[0] = TableOrSubqueryNode(select_statement=p[2])
        else:
            p[0] = TableOrSubqueryNode(table_name=p[1], table_alias=p[3])
    elif len(p) == 5:
        p[0] = TableOrSubqueryNode(select_statement=p[2], table_alias=p[4])
    else:
        p[0] = TableOrSubqueryNode(select_statement=p[2], table_alias=p[5])


def p_table_name(p):
    '''table_name : ID
                  | STRING'''
    p[0] = TerminalNode('table_name', p[1])


def p_table_alias(p):
    '''table_alias : ID
                   | STRING '''
    p[0] = TerminalNode('table_alias', p[1])


def p_join_clause(p):
    '''join_clause : table_or_subquery join_op table_or_subquery join_constraint
		| table_or_subquery join_op table_or_subquery
		| join_clause join_op table_or_subquery join_constraint
		| join_clause join_op table_or_subquery'''

    if isinstance(p[1], TableOrSubqueryNode):
        if len(p) == 5:
            p[0] = JoinClauseNode([p[1], p[3]], [p[2]], [p[4]])
        else:
            p[0] = JoinClauseNode([p[1], p[3]], [p[2]], [None])
    else:
        if len(p) == 5:
            p[0] = p[1].add_table(p[3], (p[2]), p[4])
        else:
            p[0] = p[1].add_table(p[3], (p[2]), None)


def p_join_constraint(p):
    '''join_constraint : ON expr'''
    p[0] = JoinConstraintNode(p[2])


def p_where_clause(p):
    '''where_clause : WHERE expr'''
    p[0] = WhereClauseNode(p[2])


def p_group_clause(p):
    '''group_clause : GROUP BY expr
                    | group_clause COMMA expr
                    | group_clause HAVING expr'''
    if not isinstance(p[1], GroupClauseNode):
        p[0] = GroupClauseNode([p[3]])
    else:
        if p[2] == ',':
            p[0] = p[1] + p[3]
        else:
            p[0] = replace(p[1], having=p[3])


def p_column(p):
    '''column : column_name
              | table_name DOT column_name'''

    if len(p) == 2:
        p[0] = ColumnNode(p[1])
    else:
        p[0] = ColumnNode(p[3], p[1])


def p_fun_expr(p):
    '''fun_expr : EXISTS LPAREN select_statement RPAREN
                | fun_name LPAREN expr RPAREN
                | NOT EXISTS LPAREN select_statement RPAREN
                | fun_name LPAREN DISTINCT expr RPAREN
                | fun_name LPAREN expr COMMA expr RPAREN
                | fun_name LPAREN expr COMMA expr COMMA expr RPAREN
            '''
    if len(p) == 5:
        if isinstance(p[3], SelectStatementNode):
            p[0] = FunctionExpressionNode(TerminalNode('fun_name', p[1]), [p[3]])
        else:
            p[0] = FunctionExpressionNode(p[1], [p[3]])
    elif len(p) == 6:
        if isinstance(p[4], SelectStatementNode):
            p[0] = FunctionExpressionNode(TerminalNode('fun_name', p[2]), [p[4]], negation=True)
        else:
            p[0] = FunctionExpressionNode(p[1], [p[4]], distinct=True)
    elif len(p) == 7:
        if isinstance(p[3], SelectStatementNode):
            p[0] = FunctionExpressionNode(p[1], [p[3],p[5]])
    elif len(p) == 8:
        if isinstance(p[3], SelectStatementNode):
            p[0] = FunctionExpressionNode(p[1], [p[3],p[5], p[7]])



# expr bin_op expr
def p_bin_op_expr(p):
    '''bin_op_expr : expr AND expr
                   | expr OR expr
                   | expr ARITH_OP expr
                   | expr LIKE expr
                   | expr COMP_OP expr
                   | expr IS NULL
                   | expr NOT LIKE expr
                   | expr IS NOT NULL
                   | expr IN LPAREN select_statement RPAREN
                   | expr NOT IN LPAREN select_statement RPAREN'''
    if len(p) == 4:
        if p[3] == 'null':
            p[0] = BinOpExpressionNode(p[1], TerminalNode('bin_op', p[2]), LiteralNode('NULL'))
        else:
            p[0] = BinOpExpressionNode(p[1], TerminalNode('bin_op', p[2]), p[3])
    elif len(p) == 5:
        if p[3] == 'null':
            p[0] = BinOpExpressionNode(p[1], TerminalNode('bin_op', p[2]), LiteralNode('NOT NULL'))
        else:
            p[0] = BinOpExpressionNode(p[1], TerminalNode('bin_op', 'NOT LIKE'), p[4])
    elif len(p) == 6:
        p[0] = BinOpExpressionNode(p[1], TerminalNode('bin_op', 'IN'), p[4])
    elif len(p) == 7:
        p[0] = BinOpExpressionNode(p[1], TerminalNode('bin_op', 'NOT IN'), p[5])



def p_expr(p):
    '''expr : column
            | LPAREN select_statement RPAREN
            | LPAREN expr RPAREN
            | literal_value
            | expr STAR expr
            | bin_op_expr
            | fun_expr
            | between_expr
            | cast_expr
            | win_expr
            | case_expr
            '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = p[2]


def p_set_op(p):
    '''set_op : UNION
              | EXCEPT
              | INTERSECT'''
    p[0] = TerminalNode('set_op', p[1])


def p_sort_order(p):
    '''sort_order : ASC
                  | DESC'''
    p[0] = TerminalNode('sort_order', p[1])


def p_bin_op(p):
    '''bin_op : ARITH_OP
              | COMP_OP
              | AND
              | OR
              | LIKE'''
    p[0] = TerminalNode('bin_op', p[1])

def p_join_op(p):
    '''join_op : JOIN
               | INNER JOIN
               | LEFT JOIN'''
    if len(p) == 2:
        p[0] = TerminalNode('join_op', p[1])
    else:
        p[0] = TerminalNode('join_op', p[1]+" "+p[2])


def p_type_name(p):
    '''type_name : REAL
                 | FLOAT
                 | INTEGER'''
    p[0] = TerminalNode('type_name', p[1])



def p_cast_expr(p):
    '''cast_expr : CAST LPAREN expr AS type_name RPAREN'''
    p[0] = CastExpressionNode(p[3], p[5])


def p_between_expr(p):
    '''between_expr : expr BETWEEN expr bin_op expr'''
    p[0] = BetweenExpressionNode(p[1], p[3], p[5])

def p_column_alias(p):
    '''column_alias : ID'''
    p[0] = TerminalNode('column_alias', p[1])


def p_fun_name(p):
    '''fun_name : ID'''
    p[0] = TerminalNode('fun_name', p[1])


def p_literal_value(p):
    '''literal_value : NUMBER
                     | STRING'''
    p[0] = LiteralNode(p[1])


def p_column_name(p):
    '''column_name : ID
                   | STRING
                   | STAR'''
    p[0] = TerminalNode('column_name', p[1])


def p_win_expr(p):
    # '''win_expr : win_fun LPAREN RPAREN OVER LPAREN win_def RPAREN'''
    '''win_expr : win_fun LPAREN RPAREN OVER LPAREN win_def RPAREN'''
    p[0] = WindowExpressionNode(p[1] , p[6])

def p_win_def(p):
    '''win_def : order_by
                 | PARTITION BY result_column order_by'''
    if len(p) == 2:
        p[0] = WindowDefinitionNode(p[1])
    else:
        p[0] = WindowDefinitionNode(p[4] , p[3])

def p_win_fun(p):
    '''win_fun : RANK
               | DENSE_RANK'''
    p[0] = TerminalNode('win_fun_name', p[1])


def p_case_expr(p):
    '''case_expr : CASE WHEN expr THEN expr ELSE expr END
                 | CASE WHEN expr THEN expr END'''
    if len(p) == 7:
        p[0] = FunctionExpressionNode(TerminalNode('fun_name', 'case'),[p[3], p[5]])
    else:
        p[0] = FunctionExpressionNode(TerminalNode('fun_name', 'case'), [p[3], p[5], p[7]])

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")
    print(f"Invalid token:{p}")
    raise SyntaxError(f"{p}")





def get_parser():
    parser = yacc.yacc()
    return parser




class SqlParser:
    def __init__(self):
        self.lexer = get_lexer()
        self.parser = get_parser()

    def parse(self, sql: str) -> SelectStatementNode:
        ast = self.parser.parse(sql)
        if ast:
            #FIXME: Set raw sql
            pass
        return ast
