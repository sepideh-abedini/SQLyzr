import json
from typing import Dict, Union

import yaml


class DatabaseSchema:
    tables: Dict[str, Dict[str, Union[str, Dict[str, str]]]]

    def __init__(self):
        self.tables = {}

    def to_yaml(self) -> str:
        return yaml.dump(self.tables)


def get_dbs(tables_json_path: str) -> Dict[str, DatabaseSchema]:
    dbs = dict()
    with open(tables_json_path) as file:
        data = json.load(file)
        for db in data:
            schema = DatabaseSchema()
            for table in db['table_names_original']:
                schema.tables[table.lower()] = {}
            for i, col in enumerate(db['column_names_original']):
                table_idx = col[0]
                if table_idx >= 0:
                    table_name = db['table_names_original'][table_idx].lower()
                    col_name = col[1].lower()
                    schema.tables[table_name][col_name] = db['column_types'][i]
            for foreign_keys in db['foreign_keys']:
                src_col_idx = foreign_keys[0]
                src_table_idx, src_col_name = db['column_names_original'][src_col_idx]
                src_col_name = src_col_name.lower()
                src_table_name = db['table_names_original'][src_table_idx].lower()

                dst_col_idx = foreign_keys[1]
                dst_table_idx, dst_col_name = db['column_names_original'][dst_col_idx]
                dst_col_name = dst_col_name.lower()
                dst_table_name = db['table_names_original'][dst_table_idx].lower()

                col_type = schema.tables[src_table_name][src_col_name]
                schema.tables[src_table_name][src_col_name] = {
                    "type": col_type,
                    "foreign_key": f"{dst_table_name}.{dst_col_name}"
                }

            dbs[db['db_id']] = schema
    return dbs
