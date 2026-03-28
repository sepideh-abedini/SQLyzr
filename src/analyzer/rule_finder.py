from src.analyzer.fix_evaluator import FixFinder
from src.analyzer.fix_finder import FixRule
from src.analyzer.letter_casing_transformer import all_subsets, SqlTransformer, \
    LetterCasingTransformer
from src.analyzer.limit_fixing_transformer import FixPredLimitTransformer
from src.db.sqlite_facade import SqliteFacade
from src.eval.dataset_config import DatasetConfig

ALL_TRANSFORMERS = [
    LetterCasingTransformer(),
    FixPredLimitTransformer()
]


class RuleFinder:
    ds_conf: DatasetConfig
    trs_sets: set[frozenset[SqlTransformer]]
    rule_sets = set[frozenset[FixRule]]

    def __init__(self, ds_conf: DatasetConfig, trs_sets: set[frozenset[SqlTransformer]] = all_subsets(ALL_TRANSFORMERS),
                 rule_sets: set[frozenset[FixRule]] = FixRule.all_subsets()):
        self.ds_conf = ds_conf
        self.dbf = SqliteFacade(self.ds_conf)
        self.trs_sets = trs_sets.union(frozenset({frozenset()}))
        self.rule_sets = rule_sets.union(frozenset({frozenset()}))

    def check_rules(self, pred_sql, gold_sql, db_id, trs_sub: frozenset[SqlTransformer], rule_sub: frozenset[FixRule]):
        finder = FixFinder(self.ds_conf, trs_sub, rule_sub)
        if len(rule_sub.union(trs_sub)) == 0:
            strict_match = finder.evaluate_strict(db_id, pred_sql, gold_sql)
            if strict_match:
                return rule_sub
            else:
                return None
        match = finder.evaluate(db_id, pred_sql, gold_sql)
        if match:
            return rule_sub.union(trs_sub)
        return None

    def find_rules(self, pred_sql, gold_sql, db_id):
        pred_res = self.dbf.exec_query_sync(db_id, pred_sql)
        gold_res = self.dbf.exec_query_sync(db_id, gold_sql)

        if pred_res is None or gold_res is None:
            return None

        all_trs_sets = sorted(self.trs_sets, key=len)
        all_rule_sets = sorted(self.rule_sets, key=len)
        for trs_set in all_trs_sets:
            for rules in all_rule_sets:
                rules = frozenset(rules)
                working_rules = self.check_rules(pred_sql, gold_sql, db_id, trs_set, rules)
                if working_rules is not None:
                    return working_rules
        return None
