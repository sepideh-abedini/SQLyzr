import types
import inspect
import re
import src.sql_parser.parser as parser

GRAMMAR_FILE_PATH = "out/grammar.bnf"

source = inspect.getsource(parser)


def ply_to_bnf(ply_rule: str):
    rule = ply_rule.replace('\n', ' ')
    rule = re.sub(r'\s+', ' ', rule)
    rule = rule.replace(":", "::=")
    if len(rule) > 80:
        rule = "\n\t\t|".join(rule.split("|"))
    return rule


def main():
    funs = []

    for f_name in dir(parser):
        fun = getattr(parser, f_name)
        if (isinstance(fun, types.FunctionType)
                and fun.__module__ == parser.__name__
                and fun.__name__.startswith('p_')
        ):
            line_number = inspect.getsourcelines(fun)[1]
            funs.append((line_number, fun))

    funs.sort()

    grammar = "\n".join([ply_to_bnf(f[1].__doc__) for f in funs if f[1].__doc__])

    with open(GRAMMAR_FILE_PATH, 'w') as file:
        file.write(grammar)


if __name__ == '__main__':
    main()
