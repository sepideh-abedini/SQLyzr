import json

class TableMetadata:
    def __init__(self, table_json_path):
        self.table_json_path = table_json_path
        self.tables = {}
        with open (self.table_json_path, 'r') as f:
            tables_json = json.load(f)
            for table_json in tables_json:
                self.tables[table_json["db_id"]] = table_json

    def get_col_type(self, db_id, col_name):
        table = self.tables[db_id]
        # print(table['column_names'])
        for idx, col in enumerate(table['column_names']):
            if col[1] == col_name:
                return table['column_types'][idx]
            

tm = TableMetadata("../models/spider/test_data/tables.json")
t = tm.get_col_type("perpetrator", "year")
