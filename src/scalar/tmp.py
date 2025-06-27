from src.configs.datasets import SPIDER_ALL
from src.rel.db_factory import DatabaseFactory
from src.scalar.utils.db_stats import get_db_stats
from src.scalar.utils.export_ddls import apply_migration, revert_backup, export_ddl
from src.scalar.utils.gen_mig import generate_migration_script
from src.scalar.utils.insert import insert_synth_data
from src.scalar.utils.scale import gen_synth_rows
from src.scalar.utils.table_meta import save_meta
from src.util.file_utils import read_json


def main():
    db_id = "aircraft"
    scale = 1
    scale_db(db_id, scale)


def exec_queries(conf, db_id):
    data = read_json(conf.get_test_path())
    queries = list(map(lambda r: r['query'], filter(lambda r: r['db_id'] == db_id, data)))
    dbf = DatabaseFactory.get_instance(conf)
    results = []
    for sql in queries:
        res = dbf.exec_query_sync(db_id, sql)
        results.append(res)
    return results


def scale_db(db_id, scale):
    conf = SPIDER_ALL

    revert_backup(conf.get_db_path(), db_id)

    print("Before Scale:")
    get_db_stats(conf.get_db_path(), db_id)
    try:
        generate_migration_script(conf.get_db_path(), db_id)

        pre_res = exec_queries(conf, db_id)

        apply_migration(conf.get_db_path(), db_id)

        post_res = exec_queries(conf, db_id)

        for i in range(len(pre_res)):
            if set(pre_res[i]) != set(post_res[i]):
                print(f"Query {i}:")
                print(f"Before: {pre_res[i]}")
                print(f"After: {post_res[i]}")
                raise RuntimeError("Results are different after migration!")

        save_meta(conf.get_db_path(), db_id)

        gen_synth_rows(conf.get_db_path(), db_id, scale)

        insert_synth_data(conf.get_db_path(), db_id)
        print("After Scale:")
        get_db_stats(conf.get_db_path(), db_id)
        exec_queries(conf, db_id)
    except Exception as e:
        print(f"Scaling failed: {e}")
        revert_backup(conf.get_db_path(), db_id)


if __name__ == '__main__':
    main()
