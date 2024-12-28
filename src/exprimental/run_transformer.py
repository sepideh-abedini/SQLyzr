from typing import List, Tuple, Set

from src.exprimental.terminal_visitor import ValueCollector
from src.sql_parser.node import SqlAstNode


class TransformerMatcher(ResultMatcher):
    transformers: List[ResultTransformer]

    def __init__(self, in_file, db_dir):
        super().__init__(in_file=in_file, db_dir=db_dir)
        self.transformers = [
            ExtraColRemover(),
            DuplicateRemover()
        ]

    def match(self, pred: SqlData, gold: SqlData):
        if super().match(pred, gold):
            return True
        if pred.res is None:
            return False
        pred.res = frozenset(map(lambda t: frozenset(map(lambda col: str(col), t)), pred.res))
        gold.res = frozenset(map(lambda t: frozenset(map(lambda col: str(col), t)), gold.res))


def main():
    # in_file = "data/dail/dail_non_match.csv"
    in_file = "data/din/din_non_match.csv"
    db_dir = "data/spider/database"
    matcher = TransformerMatcher(in_file=in_file, db_dir=db_dir)
    match, total = matcher.run()

    print(f"{match}/{total}")


if __name__ == "__main__":
    main()
