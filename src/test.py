from util.multi_thread import NUM_THREADS

1 + 2 - 3

NUM
OP = + | -



1 + 2

expr ::= NUM | expr OP expr


NUM OP NUM OP NUM
expr OP NUM OP NUM
expr OP expr OP NUM
expr OP expr OP expr
expr OP expr
expr

def p_expr(p):
    '''expr ::= NUM
              | expr OP expr '''
    if len(p) == 1:
        return p[0]
    elif len(p) == 3:
        if p[1] == '+':
            return p[0] + p[2]
        if p[1] == '-':
            return p[0] + p[2]

    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        if p[2] == '+':
            p[0] = p[1] + p[3]
        if p[2] == '-':
            p[0] = p[1] - p[3]


