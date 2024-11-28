from typing import Dict, List, Set, Tuple, FrozenSet

from src.util.logger import log


class DatabaseSchema:
    tables: Dict[str, Dict[str, str]]  # {table_name -> {col_name -> col_type}}
    foreign_keys: Set[FrozenSet[Tuple[str, str]]]

    def __init__(self):
        self.tables = {}
        self.foreign_keys = set()

    def get_col_type(self, table_name, col_name) -> str:
        if table_name not in self.tables:
            log(f"Table not found: {table_name}")
            return 'NA'
        table = self.tables[table_name]
        if col_name in table:
            return table[col_name]
        else:
            log(f"Column not found: {col_name}")
            return 'NA'

    def get_table_name(self, col_name: str, candidate_tables: List[str]) -> str:
        """Find the table that has a column with the given name by only searching
        in tables that are given as candidate_tables."""
        matched_tables = []
        for table in candidate_tables:
            if table not in self.tables:
                log(f"Candidate table not found: {table}, Available tables: {self.tables.keys()}")
                return "NA"
            if col_name in self.tables[table]:
                matched_tables.append(table)
        if len(matched_tables) == 1:
            return matched_tables[0]
        if len(matched_tables) == 0:
            log(f"Column not found in candidate tables: {col_name}, {candidate_tables}")
        for table in self.tables:
            if col_name in self.tables[table]:
                matched_tables.append(table)
        if len(matched_tables) == 1:
            return matched_tables[0]
        if len(matched_tables) == 0:
            log(f"Column not found in candidate tables: {col_name}, {candidate_tables}")
            return "NA"
        if len(matched_tables) > 1:
            log(f"Ambiguous column name: {col_name}, matched tables: {matched_tables}")
            return matched_tables[0]

    def __str__(self):
        res = "\nTables: \n"
        for table, columns in self.tables.items():
            res += f"\tTable Name: {table}\n"
            res += f"\t\tColumns:\n"
            for col, col_type in columns.items():
                res += f"\t\t\tColumn Name: {col}, Column type: {col_type}\n"
        return res
