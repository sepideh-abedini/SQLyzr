from typing import Dict, List, Set, Tuple, FrozenSet


class DatabaseSchema:
    tables: Dict[str, Dict[str, str]]  # {table_name -> {col_name -> col_type}}
    foreign_keys: Set[FrozenSet[Tuple[str, str]]]

    def __init__(self):
        self.tables = {}
        self.foreign_keys = set()

    def get_col_type(self, table_name, col_name) -> str:
        if table_name not in self.tables:
            raise RuntimeError(f"Table not found: {table_name}")
        table = self.tables[table_name]
        if col_name not in table:
            raise RuntimeError(f"Column not found: {col_name}")
        return table[col_name]

    def get_table_name(self, col_name: str, candidate_tables: List[str]) -> str:
        """Find the table that has a column with the given name by only searching
        in tables that are given as candidate_tables."""
        matched_tables = []
        for table in candidate_tables:
            if table not in self.tables:
                raise RuntimeError(
                    f"Candidate table not found: {table}, Available tables: {self.tables.keys()}")
            if col_name in self.tables[table]:
                matched_tables.append(table)
        if len(matched_tables) == 1:
            return matched_tables[0]
        if len(matched_tables) == 0:
            raise RuntimeError(
                f"Column not found in candidate tables: {col_name}, {candidate_tables}")
        if len(matched_tables) > 1:
            raise RuntimeError(
                f"Ambiguous column name: {col_name}, matched tables: {matched_tables}")
