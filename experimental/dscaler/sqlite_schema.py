from dataclasses import dataclass, field
from enum import EnumType
from typing import Dict, Set, Optional


class ColGenType(EnumType):
    NonUniqueNonFK = 1
    NonUniqueFK = 2
    UniqueNonFK = 3
    UniqueFK = 4


@dataclass
class SqliteColumn:
    table: str
    name: str
    type: str
    pk: bool
    fk: Optional['SqliteColumn'] = None
    unique: Set['SqliteColumn'] = field(default_factory=set)

    @property
    def gen_type(self):
        if self.fk:
            if len(self.unique) > 0:
                return ColGenType.UniqueFK
            else:
                return ColGenType.NonUniqueFK
        else:
            if len(self.unique) > 0:
                return ColGenType.UniqueNonFK
            else:
                return ColGenType.NonUniqueNonFK

    def __eq__(self, other):
        if isinstance(other, SqliteColumn):
            return self.table == other.table and self.name == other.name
        return False

    def __hash__(self):
        return hash((self.table, self.name))


@dataclass(frozen=True, eq=True)
class SqliteForeignKey:
    src: SqliteColumn
    dst: SqliteColumn


@dataclass
class SqliteTableSchema:
    cols: Dict[str, SqliteColumn]


class SqliteDatabaseSchema:
    db_id: str
    tables: Dict[str, SqliteTableSchema]

    def __init__(self, db_id: str):
        self.db_id = db_id
        self.tables = dict()

    def sort_tables(self):
        dependencies = dict()
        for tname, table in self.tables.items():
            dependencies[tname] = set()
            for col in table.cols.values():
                if col.fk is not None:
                    dependencies[tname].add(col.fk.table)
        sorted_tables = []
        while len(dependencies) > 0:
            table_with_no_deps = None
            for tname, deps in dependencies.items():
                if len(deps) == 0:
                    table_with_no_deps = tname
                    break
            else:
                raise RuntimeError("Circular dependency detected")
            for tname, deps in dependencies.items():
                if table_with_no_deps in deps:
                    deps.remove(table_with_no_deps)
            del dependencies[table_with_no_deps]
            sorted_tables.append(table_with_no_deps)
        return sorted_tables


class SqliteSchema:
    dbs: Dict[str, SqliteDatabaseSchema]
