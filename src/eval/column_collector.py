from typing import cast

from src.eval.database_column import DatabaseColumn
from src.eval.sql_features import SqlFeatures
from src.parse.node import FunctionExpressionNode
from src.parse.node import ResultColumnNode
from src.parse.node import SelectStatementNode, SelectCoreNode, TableOrSubqueryNode, FromClauseNode, \
    JoinClauseNode, \
    ColumnNode, TerminalNode
from src.parse.visitor.collector_visitor import CollectorVisitor
from src.util.database_schema import DatabaseSchema
from src.util.str_utils import split_to_snake


class ColumnCollector(CollectorVisitor):
    """Collects the columns used in the statement and finds the table name
    column type using the provided schema of database (e.g. tables.json)"""

    def __init__(self, db_schema: DatabaseSchema):
        super().__init__(SqlFeatures)
        self.alias_dict_stack = []
        self.col_alias = {}
        self.all_tables = {}
        self.inline_columns = {}
        self.inline_tables = {}
        self.anon_table = False
        self.db_schema = db_schema
        self.cand_cols = set()

    def get_merged_table_dict(self):
        """Get a dict my merging all dicts in table_stack"""
        return {k: v for t in self.alias_dict_stack for k, v in t.items()}

    def resolve_table_alias(self, table: str):
        table_dict = self.get_merged_table_dict()
        if table in table_dict:
            return table_dict[table]
        else:
            return self.all_tables[table]

    def visit_select_statement(self, node: SelectStatementNode):
        # FIXME: Ignores order by columns
        features = SqlFeatures()
        self.alias_dict_stack.append({})
        for core in node.select_cores:
            features += self.visit_select_core(core)
        if node.orderby:
            features += node.orderby.accept(self)
        self.alias_dict_stack.pop()
        return features

    def visit_select_core(self, node: SelectCoreNode):
        # Each select core might have a FROM clause and each FROM clause
        # might use alias for some tables, so we need a dict that maps
        # aliases declared in FROM clause to table names. So, we need to
        # visit the FROM clause before visiting the select clause Since there
        # might be nested statements, we maintain a stack of these dicts and
        # each time we finish visiting a select_core we pop the dict, so that
        # we do not encounter conflict if aliases are reused.
        features = SqlFeatures()
        if node.from_clause:
            features += node.from_clause.accept(self)
        features += node.select_clause.accept(self)
        if node.where_clause:
            features += node.where_clause.accept(self)
        if node.group_clause:
            features += node.group_clause.accept(self)
        return features

    def add_table(self, table_node: TableOrSubqueryNode):
        if table_node.table_name:  # If table is a subquery, it doesn't have a
            # name
            if table_node.table_alias:
                table_alias = split_to_snake(table_node.table_alias.value)
                table_name = split_to_snake(table_node.table_name.value)
                self.alias_dict_stack[-1][table_alias] = table_name
                self.all_tables[table_alias] = table_name
            else:  # If table doesn't have an alias, we still add an entry
                # table -> table, so we can resolve references like
                # table.col
                table_name = split_to_snake(table_node.table_name.value)
                self.alias_dict_stack[-1][table_name] = table_name
                self.all_tables[table_name] = table_name
        elif table_node.table_alias:
            table_alias = split_to_snake(table_node.table_alias.value)
            self.inline_tables[table_alias] = []
            self.alias_dict_stack[-1][table_alias] = table_alias
            self.all_tables[table_alias] = table_alias
        elif table_node.select_statement:
            self.anon_table = True

    def visit_from_clause(self, node: FromClauseNode):
        for table_node in node.tables:
            self.add_table(table_node)
        return super().visit_from_clause(node)

    def visit_join_clause(self, node: JoinClauseNode):
        for table_node in node.tables:
            self.add_table(table_node)
        return super().visit_join_clause(node)

    def visit_result_column(self, node: ResultColumnNode):
        if node.column_alias:
            column_alias = node.column_alias.value
            if isinstance(node.expr, ColumnNode):
                self.col_alias[column_alias] = cast(ColumnNode, node.expr).column_name.value
            elif isinstance(node.expr, FunctionExpressionNode):
                expr = cast(FunctionExpressionNode, node.expr)
                if len(expr.expr) == 1 and isinstance(expr.expr[0], ColumnNode):
                    self.col_alias[column_alias] = cast(ColumnNode, expr.expr[0]).column_name.value
            else:
                self.inline_columns[column_alias] = node.expr

        return super().visit_result_column(node)

    def visit_column(self, node: ColumnNode):
        col_name = node.column_name.value.lower()
        if col_name in self.col_alias:
            col_name = self.col_alias[col_name]
        node.db_schema = self.db_schema
        if col_name == '*':
            return SqlFeatures(col_set={STAR_COLUMN})
        if node.table_name:
            table_name = self.resolve_table_alias(node.table_name.value.lower())
        elif len(self.alias_dict_stack) > 0 and len(self.alias_dict_stack[-1]) > 0:
            # If no table is specified for a column, then we need to search
            # in the list of columns of each table provided by the database
            # schema (tables.json) to find the table that has this column. We
            # should only search in tables that are listed in the FROM clause
            if len(self.alias_dict_stack[-1].values()) == 1:
                table_name = list(self.alias_dict_stack[-1].values())[0]
            else:
                table_name = self.db_schema.get_table_name(col_name, self.alias_dict_stack[-1].values())
        else:
            table_name = self.db_schema.get_table_name(col_name, list(self.all_tables.values()))
        node.table_name = TerminalNode('table_name', table_name)
        col_type = self.db_schema.get_col_type(table_name, col_name)

        return SqlFeatures(
            col_set={DatabaseColumn(table_name, col_name, col_type)})
