from src.sql_parser.node import LiteralNode, ExpressionNode, TerminalNode, BinOpExpressionNode, FunctionExpressionNode, \
    ColumnNode, ResultColumnNode, TableOrSubqueryNode, JoinConstraintNode, JoinClauseNode, LimitNode, OrderingTerm, \
    OrderByNode, BetweenExpressionNode, WhereClauseNode, FromClauseNode, GroupClauseNode, SelectClauseNode, \
    SelectCoreNode, SelectStatementNode
from src.visitor.node_visitor import NodeVisitor


class StringVisitor(NodeVisitor):
    cur_level: int

    def __init__(self):
        self.cur_level = 0

    def visit_select_statement(self, node: SelectStatementNode):
        self.cur_level += 1
        result = node.select_cores[0].accept(self)
        if len(node.select_cores) > 1:
            for core, op in zip(node.select_cores[1:], node.set_ops):
                result += f" {op.accept(self)} {core.accept(self)}"
        if node.orderby:
            result += f" {node.orderby.accept(self)}"
        if node.limit:
            result += f" {node.limit.accept(self)}"
        self.cur_level -= 1
        if self.cur_level > 0:
            return f"({result})"
        else:
            return result

    def visit_select_core(self, node: SelectCoreNode):
        result = node.select_clause.accept(self)
        result += f" {node.from_clause.accept(self)}"
        if node.where_clause:
            result += f" {node.where_clause.accept(self)}"
        if node.group_clause:
            result += f" {node.group_clause.accept(self)}"
        return result

    def visit_select_clause(self, node: SelectClauseNode):
        result = "SELECT "
        if node.distinct:
            result += "DISTINCT "
        col_strs = list(map(lambda col: col.accept(self), node.result_columns))
        # sorted_cols = sorted(node.result_columns, key=lambda col: 1)
        col_strs = sorted(col_strs)
        result += ','.join(col for col in col_strs)
        return result

    def visit_group_clause(self, node: GroupClauseNode):
        result = "GROUP BY "
        result += ','.join([e.accept(self) for e in node.exprs])
        if node.having:
            result += f" HAVING {node.having.accept(self)}"
        return result

    def visit_from_clause(self, node: FromClauseNode):
        result = "FROM "
        if node.join_clause:
            result += node.join_clause.accept(self)
        else:
            result += ','.join([t.accept(self) for t in node.tables])
        return result

    def visit_where_clause(self, node: WhereClauseNode):
        result = "WHERE "
        result += node.expr.accept(self)
        return result

    def visit_between_expression(self, node: BetweenExpressionNode):
        return (f"{node.expr.accept(self)}"
                f" BETWEEN {node.lower.accept(self)}"
                f" AND {node.upper.accept(self)}")

    def visit_order_by(self, node: OrderByNode):
        return f"ORDER BY {','.join([t.accept(self) for t in node.ordering_terms])}"

    def visit_ordering_term(self, node: OrderingTerm):
        result = node.expr.accept(self)
        if node.sort_order:
            result += f" {node.sort_order.accept(self)}"
        return result

    def visit_limit(self, node: LimitNode):
        return f"LIMIT {node.expr.accept(self)}"

    def visit_join_clause(self, node: JoinClauseNode):
        result = node.tables[0].accept(self)
        result += "".join([f" JOIN {t.accept(self)} {c.accept(self) if c else ''}" for t, c in
                           zip(node.tables[1:], node.constraints)])
        return result

    def visit_join_constraint(self, node: JoinConstraintNode):
        return f"ON {node.expr.accept(self)}"

    def visit_table_or_subquery(self, node: TableOrSubqueryNode):
        if node.table_name:
            result = node.table_name.accept(self)
        else:
            result = node.select_statement.accept(self)
        if node.table_alias:
            result += f" AS {node.table_alias.accept(self)}"
        return result

    def visit_result_column(self, node: ResultColumnNode):
        result = node.expr.accept(self)
        if node.column_alias:
            result += f" AS {node.column_alias.accept(self)}"
        return result

    def visit_column(self, node: ColumnNode):
        result = ""
        if node.table_name:
            result += f"{node.table_name.accept(self)}."
        result += node.column_name.accept(self)
        return result

    def visit_function_expression(self, node: FunctionExpressionNode):
        result = ""
        if node.negation:
            result += "NOT "
        result += f"{node.fun_name.accept(self)}("
        if node.distinct:
            result += "DISTINCT "
        result += f"{node.expr.accept(self)})"
        return result

    def visit_bin_op_expression(self, node: BinOpExpressionNode):
        result = f"{node.left.accept(self)}"
        result += f" {node.op.accept(self)}"
        result += f" {node.right.accept(self)}"
        return result

    def visit_terminal(self, node: TerminalNode):
        return str(node.value)

    def visit_expression(self, node: ExpressionNode):
        pass

    def visit_literal(self, node: LiteralNode):
        return str(node.value)
