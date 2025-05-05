import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import EnumType, Enum
from typing import Dict, Set, List, Tuple

from experimental.dscaler.sqlite_db import SqliteDatabase
from experimental.dscaler.sqlite_interface import SqliteInterface
from experimental.dscaler.sqlite_schema import SqliteDatabaseSchema, SqliteTableSchema, ColGenType, SqliteColumn
from experimental.dscaler.sqlite_schema_factory import SqliteSchemaFactory


class ValueType(Enum):
    INT = 1
    TEXT = 2

    @staticmethod
    def from_str(s: str) -> 'ValueType':
        match s:
            case "INT":
                return ValueType.INT
            case "TEXT":
                return ValueType.TEXT
            case _:
                raise RuntimeError(f"Unsupported type: {s}")


class ColumnValueGenerator(ABC):
    @abstractmethod
    def gen(self) -> Tuple:
        pass


class PoolValueGenerator(ColumnValueGenerator):
    pool: Set

    def __init__(self, pool: Set):
        self.pool = pool

    def gen(self) -> Tuple:
        return tuple([random.choice(list(self.pool))])


class RandomValueGenerator(ColumnValueGenerator):
    type: ValueType

    def __init__(self, value_type: ValueType):
        self.type = value_type

    def gen(self) -> Tuple:
        match self.type:
            case ValueType.INT:
                return tuple([random.randint(1, 100)])
            case ValueType.TEXT:
                return tuple("rand")
            case _:
                raise RuntimeError(f"Unsupported type: {self.type}")


class UniqueValueGenerator(RandomValueGenerator):
    pool: Set

    def __init__(self, value_type: ValueType, pool: Set):
        super().__init__(value_type)
        self.pool = pool

    def gen(self) -> Tuple:
        while True:
            val = super().gen()
            if val not in self.pool:
                return tuple(val)


class TupleGenerator(ColumnValueGenerator):
    cols: List[SqliteColumn]
    generators: List[ColumnValueGenerator]

    def __init__(self, cols: List[SqliteColumn], generators: List[ColumnValueGenerator]):
        self.cols = cols
        self.generators = generators

    @abstractmethod
    def gen(self) -> Tuple:
        pass


class UniqueTupleGenerator(TupleGenerator):
    pool: Set[Tuple]

    def __init__(self, cols: List[SqliteColumn], generators: List[ColumnValueGenerator], pool: Set[Tuple]):
        super().__init__(cols, generators)
        self.pool = pool

    def gen_rand_tuple(self) -> Tuple:
        t = tuple()
        for gen in self.generators:
            t = t + gen.gen()
        return tuple(t)

    def gen(self):
        while True:
            t = self.gen_rand_tuple()
            if t not in self.pool:
                return t


class ValueGeneratorFactory:
    db_id: str
    interface: SqliteInterface

    def __init__(self, db_id: str, interface: SqliteInterface):
        self.db_id = db_id
        self.interface = interface

    def get_generator(self, col: SqliteColumn) -> ColumnValueGenerator:
        if len(col.unique) == 0:
            if col.fk:
                pool = self.interface.get_col_vals(self.db_id, col.fk.table, col.fk.name)
                return PoolValueGenerator(pool)
            else:
                pool = self.interface.get_col_vals(self.db_id, col.table, col.name)
                return PoolValueGenerator(pool)
        elif len(col.unique) == 1:
            if col.fk:
                pool = self.interface.get_col_vals(self.db_id, col.fk.table, col.fk.name)
                existing_pool = self.interface.get_col_vals(self.db_id, col.table, col.name)
                return PoolValueGenerator(pool.difference(existing_pool))
            else:
                pool = self.interface.get_col_vals(self.db_id, col.table, col.name)
                return UniqueValueGenerator(ValueType.from_str(col.type), pool)
        raise RuntimeError(f"Unsupported column type: {col.type}")

    def get_tuple_generator(self, cols: List[SqliteColumn]) -> TupleGenerator:
        assert len(cols) > 0
        generators = []
        for col in cols:
            if col.fk:
                pool = self.interface.get_col_vals(self.db_id, col.fk.table, col.fk.name)
                generator = PoolValueGenerator(pool)
            else:
                generator = RandomValueGenerator(ValueType.from_str(col.type))
            generators.append(generator)
        col_names = [col.name for col in cols]
        table_name = cols[0].table
        pool = self.interface.get_col_list_vals(self.db_id, table_name, col_names)
        return UniqueTupleGenerator(cols, generators, pool)


@dataclass
class ColSetValGen:
    cols: List[SqliteColumn]
    val_gen: ColumnValueGenerator


class SqliteScaler:
    db: SqliteDatabase
    interface: SqliteInterface

    def __init__(self, db_path: str, scale_factor: int):
        orig_db = SqliteDatabase(db_path)
        self.db = orig_db.copy(f"X{scale_factor}")
        self.interface = SqliteInterface(self.db)
        self.scale_factor = scale_factor

    def print_stats(self):
        for db_id, table in self.db_id_tables:
            num_rows = self.interface.get_num_rows(db_id, table)
            print(f"{db_id}:{table} = {num_rows}")

    @property
    def db_id_tables(self):
        res = []
        for db_id in self.db.db_ids:
            tables = self.interface.get_tables(db_id)
            for table in tables:
                res.append((db_id, table))
        return res

    def scale(self, db_id: str):
        factory = SqliteSchemaFactory(self.db)
        db_schema = factory.process_db(db_id)
        for table_schema in db_schema.tables.values():
            rows = self.scale_table(db_schema, table_schema)
            print(rows)
            # break

    def scale_table(self, db_schema: SqliteDatabaseSchema, table_schema: SqliteTableSchema):
        new_rows = []
        for i in range(self.scale_factor):
            row = self.gen_row(db_schema, table_schema)
            new_rows.append(row)
            break
        return new_rows

    def gen_row(self, db_schema: SqliteDatabaseSchema, table_schema: SqliteTableSchema):
        row = {}
        val_gen_factory = ValueGeneratorFactory(db_schema.db_id, self.interface)

        seen_cols = set()
        gens: List[ColSetValGen] = []
        for col in table_schema.cols.values():
            if col in seen_cols:
                continue
            if len(col.unique) <= 1:
                gen = ColSetValGen([col], val_gen_factory.get_generator(col))
                gens.append(gen)
                seen_cols.add(col)
            else:
                cols_ordered = list(col.unique)
                gen = ColSetValGen(cols_ordered, val_gen_factory.get_tuple_generator(cols_ordered))
                gens.append(gen)
                seen_cols.update(col.unique)

        for gen in gens:
            keys = gen.cols
            values = gen.val_gen.gen()
            for i, key in enumerate(keys):
                row[key.name] = values[i]

        if len(row) != len(table_schema.cols):
            raise RuntimeError("Row generation failed")
        return row
