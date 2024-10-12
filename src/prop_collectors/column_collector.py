from src.sql_parser.node import ResultColumnNode
from src.sql_parser.node import SelectStatementNode, SelectCoreNode, TableOrSubqueryNode, FromClauseNode, JoinClauseNode, \
    ColumnNode, TerminalNode
from src.dbutil.database_schema import DatabaseSchema
from src.prop_collectors.sql_features import SqlFeatures
from src.prop_collectors.database_column import DatabaseColumn, STAR_COLUMN
from src.visitor.collector_visitor import CollectorVisitor


class ColumnCollector(CollectorVisitor):
    """Collects the columns used in the statement and finds the table name
    column type using the provided schema of database (e.g. tables.json)"""

    def __init__(self, db_schema: DatabaseSchema):
        super().__init__(SqlFeatures)
        self.alias_dict_stack = []
        self.all_tables = {}
        self.db_schema = db_schema

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
        for core in node.select_cores:
            features += self.visit_select_core(core)
        if node.orderby:
            features += node.orderby.accept(self)
        return features

    def visit_select_core(self, node: SelectCoreNode):
        # Each select core might have a FROM clause and each FROM clause
        # might use alias for some tables, so we need a dict that maps
        # aliases declared in FROM clause to table names. So, we need to
        # visit the FROM clause before visiting the select clause Since there
        # might be nested statements, we maintain a stack of these dicts and
        # each time we finish visiting a select_core we pop the dict, so that
        # we do not encounter conflict if aliases are reused.
        self.alias_dict_stack.append({})
        features = SqlFeatures()
        features += node.from_clause.accept(self)
        features += node.select_clause.accept(self)
        if node.where_clause:
            features += node.where_clause.accept(self)
        if node.group_clause:
            features += node.group_clause.accept(self)
        self.alias_dict_stack.pop()
        return features

    def add_table(self, table_node: TableOrSubqueryNode):
        if table_node.table_name:  # If table is a subquery, it doesn't have a
            # name
            if table_node.table_alias:
                self.alias_dict_stack[-1][
                    table_node.table_alias.value] = table_node.table_name.value
                self.all_tables[table_node.table_alias.value] = table_node.table_name.value
            else:  # If table doesn't have an alias, we still add an entry
                # table -> table, so we can resolve references like
                # table.col
                self.alias_dict_stack[-1][
                    table_node.table_name.value] = table_node.table_name.value
                self.all_tables[table_node.table_name.value] = table_node.table_name.value



    def visit_from_clause(self, node: FromClauseNode):
        for table_node in node.tables:
            self.add_table(table_node)
        return super().visit_from_clause(node)

    def visit_join_clause(self, node: JoinClauseNode):
        for table_node in node.tables:
            self.add_table(table_node)
        return super().visit_join_clause(node)

    def visit_column(self, node: ColumnNode):
        col_name = node.column_name.value
        node.db_schema = self.db_schema
        if col_name == '*':
            return SqlFeatures(col_set={STAR_COLUMN})
        if node.table_name:
            table_name = self.resolve_table_alias(node.table_name.value)
        elif len(self.alias_dict_stack) > 0:
            # If no table is specified for a column, then we need to search
            # in the list of columns of each table provided by the database
            # schema (tables.json) to find the table that has this column. We
            # should only search in tables that are listed in the FROM clause
            table_name = self.db_schema.get_table_name(col_name,
                                                       self.alias_dict_stack[
                                                           -1].values())
        else:
            table_name = self.db_schema.get_table_name(col_name, list(self.all_tables.values()))
        node.table_name = TerminalNode('table_name', table_name)
        col_type = self.db_schema.get_col_type(table_name, col_name)
        return SqlFeatures(
            col_set={DatabaseColumn(table_name, col_name, col_type)})
