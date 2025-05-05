from experimental.dscaler.sqlite_db import SqliteDatabase
from experimental.dscaler.sqlite_interface import SqliteInterface
from experimental.dscaler.sqlite_schema import SqliteTableSchema, SqliteDatabaseSchema, SqliteForeignKey


class SqliteSchemaFactory:
    def __init__(self, db: SqliteDatabase):
        self.interface = SqliteInterface(db)

    def process_table(self, db_id, table) -> SqliteTableSchema:
        cols = self.interface.get_cols(db_id, table)
        table_schema = SqliteTableSchema(cols)
        indexes = self.interface.get_indexes(db_id, table)
        unique_indexes = [idx for idx in indexes if idx.unique]
        for idx in unique_indexes:
            cols = self.interface.get_index_cols(db_id, idx.name)
            cols = {table_schema.cols[col] for col in cols}
            for col in cols:
                col.unique = cols
        return table_schema

    def process_db(self, db_id) -> SqliteDatabaseSchema:
        tables = self.interface.get_tables(db_id)
        db_schema = SqliteDatabaseSchema(db_id)
        for table in tables:
            table_schema = self.process_table(db_id, table)
            db_schema.tables[table] = table_schema

        for table in tables:
            fks = self.interface.get_foreign_key(db_id, table)
            for fk_refs in fks:
                src = db_schema.tables[fk_refs.src_table].cols[fk_refs.src_col]
                dst = db_schema.tables[fk_refs.dst_table].cols[fk_refs.dst_col]
                src.fk = dst
        return db_schema
