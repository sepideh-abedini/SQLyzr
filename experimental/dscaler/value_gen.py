from abc import ABC, abstractmethod

from experimental.dscaler.sqlite_schema import SqliteColumn


class ValueGeneratorFactory:
    def get_value_generator(self, col: SqliteColumn):
        if not col.fk and len(col.unique) == 0:
            return PoolValueGenerator()
        elif col.fk and len(col.unique) == 0:
            return PoolValueGenerator()
        elif col.fk:
            return ForeignKeyValueGenerator()
        return None


class ValueGenerator(ABC):
    @abstractmethod
    def gen_value(self, col: SqliteColumn):
        pass


class PoolValueGenerator(ValueGenerator):
    def gen_value(self, col: SqliteColumn):
        return ""


class UniqueValueGenerator(ValueGenerator):
    def gen_value(self, col: SqliteColumn):
        return ""


class ForeignKeyValueGenerator(ValueGenerator):
    def gen_value(self, col: SqliteColumn):
        return ""


class ValueGenerator:
    def gen_value(self, col: SqliteColumn):
        return ""
