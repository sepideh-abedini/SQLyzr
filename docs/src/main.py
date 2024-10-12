from docs.src.evaluator import EvaluatorVisitor
from docs.src.parser import get_parser


def main():
    parser = get_parser()
    expr = '1 + 3 - 2'
    node = parser.process(expr)

    evaluator = EvaluatorVisitor()
    result = node.accept(evaluator)

    print(f'Result: {result}')


if __name__ == '__main__':
    main()
