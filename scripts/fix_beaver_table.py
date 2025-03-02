import argparse
import copy
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple

from src.util.file_utils import read_json


@dataclass
class SchemaCol:
    name: str
    primary_key: bool = False
    type: str = 'text'

    def __init__(self, name: str, primary_key: bool):
        self.name = name
        self.primary_key = primary_key


class SchemaTable:
    name: str
    cols: List[SchemaCol]
    fks: Dict[str, Tuple[str, str]]

    def __init__(self, name: str):
        self.name = name
        self.cols = []
        self.fks = dict()


class SchemaDB:
    db_id: str
    tables: List[SchemaTable]

    def __init__(self, db_id: str):
        self.db_id = db_id
        self.tables = []

    def data(self):
        d = {
            "db_id": self.db_id,
            'table_names': [],
            'column_names': [
                [-1, '*']
            ],
            'column_types': [
                'text'
            ],
            'primary_keys': [

            ],
            'foreign_keys': [

            ]
        }
        col_idx = 1
        col_to_idx = dict()
        for i, table in enumerate(self.tables):
            d['table_names'].append(table.name)
            pkeys = []
            for col in table.cols:
                col_to_idx[(table.name, col.name)] = col_idx
                d['column_names'].append([i, col.name])
                d['column_types'].append(col.type)
                if col.primary_key:
                    pkeys.append(col_idx)
                col_idx += 1
            if len(pkeys) == 1:
                d['primary_keys'].append(pkeys[0])
            else:
                d['primary_keys'].append(pkeys)

        for i, table in enumerate(self.tables):
            for c, (rt, rc) in table.fks.items():
                ci = col_to_idx[table.name, c]
                ri = col_to_idx[rt, rc]
                d['foreign_keys'].append([ci, ri])

        d['table_names_original'] = copy.deepcopy(d['table_names'])
        d['column_names_original'] = copy.deepcopy(d['column_names'])

        return d


class BeaverSchema:
    dbs: Dict[str, SchemaDB]

    def __init__(self):
        self.dbs = dict()

    def data(self):
        res = []
        for db in self.dbs.values():
            res.append(db.data())
        return res

    def export(self, out: str):
        data = self.data()
        with open(out, "w") as file:
            file.write(json.dumps(data, indent=4))


def create_schema(tables_path):
    tables = read_json(tables_path)
    dbs = set(map(lambda t: t['db_id'], tables.values()))
    schema = BeaverSchema()
    for db in dbs:
        schema.dbs[db] = SchemaDB(db)

    for entry in tables.values():
        ta = SchemaTable(entry['table_name_original'])
        for n, t in zip(entry['column_names_original'], entry['column_types']):
            is_pk = n in entry['primary_key'] if 'primary_key' in entry else False
            ta.cols.append(SchemaCol(n, is_pk))
        if 'foreign_key' in entry:
            for fk in entry['foreign_key']:
                ref_t = fk['referenced_table_name'].split("#")[2]
                ta.fks[fk['column_name']] = (ref_t, fk['referenced_column_name'])

        schema.dbs[entry['db_id']].tables.append(ta)
    return schema


# FIXME: Fix datatypes
def convert(in_file, out_file):
    schema = create_schema(in_file)
    schema.export(out_file)


def main(in_file, out_file):
    convert(in_file, out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
