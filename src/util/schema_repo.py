import json
from typing import Dict

from loguru import logger

from src.util.database_schema import DatabaseSchema, TableSchema
from src.util.str_utils import split_to_snake


class DatabaseSchemaRepo:
    dbs: Dict[str, DatabaseSchema]

    def __init__(self, tables_json_path: str):
        self.dbs = {}
        with open(tables_json_path) as file:
            data = json.load(file)
            for db in data:
                schema = DatabaseSchema(db['db_id'])
                for table in db['table_names_original']:
                    table = split_to_snake(table)
                    schema.tables[table.lower()] = TableSchema()
                for i, col in enumerate(db['column_names_original']):
                    table_idx = col[0]
                    if table_idx >= 0:
                        table_name = split_to_snake(
                            db['table_names_original'][table_idx])
                        col_name = col[1].lower()
                        schema.tables[table_name].columns[col_name] = \
                            db['column_types'][i]
                for foreign_keys in db['foreign_keys']:
                    src_col_idx = foreign_keys[0]
                    dst_col_idx = foreign_keys[1]
                    src_table_idx, src_col_name = db['column_names_original'][src_col_idx]
                    dst_table_idx, dst_col_name = db['column_names_original'][dst_col_idx]
                    src_table_name = split_to_snake(db['table_names_original'][src_table_idx])
                    dst_table_name = split_to_snake(db['table_names_original'][dst_table_idx])
                    fk = ((src_table_name, src_col_name), (dst_table_name, dst_col_name))
                    schema.foreign_keys.add(fk)

                for table_idx, primary_keys in enumerate(db['primary_keys']):
                    table_name_original = db['table_names_original'][table_idx]
                    table_name = split_to_snake(table_name_original)
                    pks = set()
                    if isinstance(primary_keys, int):
                        col_idx = primary_keys
                        col_name = db['column_names_original'][col_idx][1]
                        pks.add(col_name.lower())
                    if isinstance(primary_keys, list):
                        for pk in primary_keys:
                            col_name = db['column_names_original'][pk][1]
                            pks.add(col_name.lower())
                    schema.tables[table_name].primary_keys = pks

                self.dbs[db['db_id']] = schema

    def get_db_id_with_most_columns(self):
        best_db_id = None
        max_cols = 0
        for db_id, schema in self.dbs.items():
            num_cols = sum(len(table.keys()) for table in schema.tables.values())
            if num_cols > max_cols:
                max_cols = num_cols
                best_db_id = db_id
        logger.info(f"DB with most columns: {best_db_id}:{max_cols}")
        return best_db_id
