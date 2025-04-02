from src.configs.datasets import BEAVER_ALL, BIRD_ALL
from src.rel.db_factory import DatabaseFactory

conf = BIRD_ALL
db_id = "movie_platform"

dbf = DatabaseFactory.get_instance(conf)

tables = dbf.get_tables(db_id)

print(tables)
print("\nColumns")
for t in tables:
    print(dbf.get_col_names(db_id, t))

print("\nPK")
for t in tables:
    print(dbf.get_primary_key(db_id, t))

print("\nFK")
for t in tables:
    print(t, dbf.get_foreign_key(db_id, t))

print("\nCT")
for t in tables:
    print(dbf.get_create_sql(db_id, t))
