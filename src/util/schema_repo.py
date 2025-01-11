import json
from os.path import split
from typing import Dict

from src.util.database_schema import DatabaseSchema
from src.util.str_utils import split_to_snake


class DatabaseSchemaRepo:
    dbs: Dict[str, DatabaseSchema]

    def __init__(self, tables_json_path: str):
        self.dbs = {}
        with open(tables_json_path) as file:
            data = json.load(file)
            for db in data:
                schema = DatabaseSchema()
                for table in db['table_names_original']:
                    table = split_to_snake(table)
                    schema.tables[table.lower()] = {}
                for i, col in enumerate(db['column_names_original']):
                    table_idx = col[0]
                    if table_idx >= 0:
                        table_name = split_to_snake(
                            db['table_names_original'][table_idx])
                        col_name = col[1].lower()
                        schema.tables[table_name][col_name] = \
                            db['column_types'][i]
                for foreign_keys in db['foreign_keys']:
                    foreign_keys_set = set()
                    for column_index in foreign_keys:
                        table_idx, col_name = db['column_names_original'][column_index]
                        col_name = col_name.lower()
                        table_name = split_to_snake(db['table_names_original'][table_idx])
                        foreign_keys_set.add((table_name, col_name))
                    schema.foreign_keys.add(frozenset(foreign_keys_set))

                self.dbs[db['db_id']] = schema

    def get_db_id_with_most_columns(self):
        best_db_id = None
        max_cols = 0
        for db_id, schema in self.dbs.items():
            num_cols = sum(len(table.keys()) for table in schema.tables.values())
            if num_cols > max_cols:
                max_cols = num_cols
                best_db_id = db_id
        print(f"DB with most columns: {best_db_id}:{max_cols}")
        return best_db_id
