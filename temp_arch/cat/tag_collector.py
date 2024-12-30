from src.cat.statement_tag import *
from src.cat.tag_collector_result import TagCollectorResult
from src.sql_parser.node import *
from src.visitor.collector_visitor import CollectorVisitor


class TagCollector(CollectorVisitor):
    def __init__(self):
        super().__init__(TagCollectorResult)


class SelectTagCollector(TagCollector):
    def visit_select_clause(self, node: SelectClauseNode):
        if len(node.result_columns) == 1:
            return TagCollectorResult(SelectType.SingleColumn)
        else:
            return TagCollectorResult(SelectType.MultiColumn)


class TableCountCollector(TagCollector):
    def __init__(self):
        super().__init__()
        self.uniq_table_names = set()

    def visit_from_clause(self, node: FromClauseNode):
        for table in node.tables:
            if table.table_name:
                self.uniq_table_names.add(table.table_name)


class WhereTagCollector(TagCollector):
    is_where_expr: bool = False

    def visit_where_clause(self, node: WhereClauseNode):
        self.is_where_expr = True
        tags = super().visit_where_clause(node)
        self.is_where_expr = False
        return tags

    def visit_bin_op_expression(self, node: BinOpExpressionNode):
        if not self.is_where_expr:
            return TagCollectorResult()
        tags = super().visit_bin_op_expression(node)
        if node.op.value.lower() not in ['and', 'or']:
            tags += TagCollectorResult(WhereType.SingleWhereExpr)
        else:
            tags += TagCollectorResult(WhereType.MultipleWhereExpr)
        return tags


class ExprTagCollector(TagCollector):
    def visit_bin_op_expression(self, node: BinOpExpressionNode):
        tags = super().visit_bin_op_expression(node)
        if node.is_arith_expr():
            return tags + TagCollectorResult(ExprType.ArithExpr)
        else:
            if not node.left.has_sub_expr() and not node.right.has_sub_expr():
                return tags + TagCollectorResult(ExprType.SingleBinExpr)
            else:
                return tags + TagCollectorResult(ExprType.ComplexExpr)

    def visit_between_expression(self, node: BetweenExpressionNode):
        tags = super().visit_between_expression(node)
        return tags + TagCollectorResult(ExprType.ComplexExpr)


class GroupTagCollector(TagCollector):
    def visit_group_clause(self, node: GroupClauseNode):
        tags = super().visit_group_clause(node)
        if node.having:
            return tags + TagCollectorResult(GroupType.ConditionalGroup)
        else:
            return tags + TagCollectorResult(GroupType.UnconditionalGroup)


class JoinTagCollector(TagCollector):
    def visit_join_clause(self, node: JoinClauseNode):
        tags = super().visit_join_clause(node)
        if any(con is not None for con in node.constraints):
            return tags + TagCollectorResult(JoinConditions.ConditionalJoin)
        else:
            return tags + TagCollectorResult(JoinConditions.UnconditionalJoin)


class JoinTablesTagCollector(TagCollector):
    def visit_join_clause(self, node: JoinClauseNode):
        tags = super().visit_join_clause(node)
        if len(node.tables) == 2:
            return tags + TagCollectorResult(JoinTables.SingleJoin)
        else:
            return tags + TagCollectorResult(JoinTables.MultiJoin)


class ExtraKeywordsTagCollector(TagCollector):
    def visit_select_clause(self, node: SelectClauseNode):
        tags = super().visit_select_clause(node)
        if node.distinct:
            return tags + TagCollectorResult(ExtraKeywords.Distinct)
        return tags

    def visit_limit(self, node: LimitNode):
        return TagCollectorResult(ExtraKeywords.Limit)

    def visit_order_by(self, node: OrderByNode):
        tags = super().visit_order_by(node)
        return tags + TagCollectorResult(ExtraKeywords.OrderBy)


class StructureTagCollector(TagCollector):
    cur_level: int

    def __init__(self):
        super().__init__()
        self.cur_level = 0

    def visit_select_statement(self, node: SelectStatementNode):
        self.cur_level += 1
        tags = super().visit_select_statement(node)
        if len(node.set_ops) > 0:
            tags += TagCollectorResult(StructureType.Compound)
        if self.cur_level > 1:
            tags += TagCollectorResult(StructureType.Nested)
        self.cur_level -= 1
        return tags
