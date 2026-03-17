import os
import shutil
from functools import partial
from multiprocessing import Pool

import pandas as pd
import tqdm
from sdv.metadata import Metadata
from sdv.multi_table import HMASynthesizer
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.utils import poc
from sdv.utils.poc import get_random_subset

from src.new_scale.data_utils import read_table_from_sqlite
from src.new_scale.db_utils import get_total_row_count


def read_total_synthetic_data(db_id):
    total_data = 0
    for f in os.listdir(f"data/database/{db_id}"):
        if f.endswith("_synthetic.csv"):
            df = pd.read_csv(f"data/database/{db_id}/{f}")
            total_data += len(df)
    # if total_data < 1000:
    #     for f in os.listdir(f"data/database/{db_id}"):
    #         if f.endswith("_synthetic.csv"):
    #             os.remove(f"data/database/{db_id}/{f}")
    print("TOTAL SYNTH DATA:", total_data)


def scale_db(db_dir: str, db_id: str, scale_size: int):
    db_file_dir = os.path.join(db_dir, db_id)
    db_file = os.path.join(db_file_dir, f"{db_id}.sqlite")
    metadata = Metadata.load_from_json(os.path.join(db_file_dir, "meta.json"))

    tables = metadata.tables.keys()

    print(f"Scaling DB: [{db_id}], tables={tables}")

    data = dict()

    for t in tqdm.tqdm(tables, total=len(tables)):
        df = read_table_from_sqlite(db_file, t)
        if db_id in big_tables and t in big_tables[db_id]:
            df = df.head(100)
        data[t] = df

    if db_id in complex_dbs:
        s_data, s_metadata = poc.simplify_schema(data, metadata)
        if db_id in main_tables:
            s_data = get_random_subset(s_data, s_metadata, main_tables[db_id], 100)
        synthesizer = HMASynthesizer(s_metadata, verbose=True)
        synthesizer.fit(s_data)
    else:
        synthesizer = HMASynthesizer(metadata, verbose=True)
        synthesizer.fit(data)

    synthetic_data = synthesizer.sample(scale=scale_size)

    print(f"Multi synth done: {db_id}")

    if db_id in complex_dbs:
        merged_dfs = dict()
        for t in s_metadata.tables:
            t_meta = metadata.tables[t]
            synthesizer = GaussianCopulaSynthesizer(t_meta)
            synthesizer.fit(data[t])
            multi_df = synthetic_data[t]
            single_df = synthesizer.sample(num_rows=len(multi_df))
            common_cols = multi_df.columns.intersection(single_df.columns)
            new_cols = single_df.drop(columns=common_cols)
            x = pd.concat([multi_df, new_cols], axis=1)
            merged_dfs[t] = x
    else:
        merged_dfs = synthetic_data

    total_data = 0
    for t, df in merged_dfs.items():
        df.to_csv(os.path.join(db_file_dir, '{t}_synthetic.csv'), index=False)
        total_data += len(df)

    before = get_total_row_count(db_file)
    new_data = total_data
    print("\n" * 10)
    print("#" * 100)
    print("*" * 100)
    print("-" * 100)
    print(f"Total synthetic data: {before} => {total_data}, {int(total_data / before)}")
    print("-" * 100)
    print("*" * 100)
    print("#" * 100)
    print("\n" * 10)


skip_dbs = {
    # "address_1",
    # "aircraft"
}

big_tables = {
    "aan_1": {"citation"}
}

main_tables = {
    "aan_1": "author_list",
    "music_1": "song",
    "formula_1": "qualifying",
    "assets_maintenance": "engineer_visits",
    "customers_and_invoices": "order_items",
    "wta_1": "rankings",
    "college_1": "enroll",
    "products_for_hire": "bookings",
    "flight_4": "routes"
}

complex_dbs = {
    "aan_1",
    "music_1",
    "formula_1",
    "assets_maintenance",
    "customers_and_invoices",
    "wta_1",
    "college_1",
    "products_for_hire",
    "tracking_grants_for_research",
    "party_people",
    "cre_Doc_Template_Mgt",
    "advertising_agencies",
    "product_catalog",
    "sakila_1",
    "orchestra",
    "real_estate_rentals",
    "customer_deliveries",
    "department_store",
    "driving_school",
    "flight_4",
    "insurance_and_eClaims",
    "insurance_policies",
    "apartment_rentals",
    "behavior_monitoring",
    "hr_1"
}


def scale_db_worker(db_id, scale_size):
    try:
        print(f"Starting Scale: {db_id}")
        scale_db(db_id, scale_size)
        return db_id, True, None
    except Exception as e:
        return db_id, False, str(e)


def main(scale_size, num_workers):
    # Get list of databases to process
    all_dbs = [d for d in os.listdir("data/database")
               if not d.startswith(".") and d not in skip_dbs]

    total = len(all_dbs)
    done = 0
    failed_dbs = []

    print(f"Starting multiprocessing pool with {num_workers} workers for {total} databases.")

    worker_func = partial(scale_db_worker, scale_size=scale_size)

    with Pool(processes=num_workers) as pool:
        results = list(tqdm.tqdm(pool.imap(worker_func, all_dbs), total=total))

    # Process results
    for db_id, success, err in results:
        # for db_id in all_dbs:
        #     timer = Timer.start()
        #     _, success, err = scale_db_worker(db_id, scale_size)
        #     scale_time = timer.lap()
        #     print(f"Scale done: {db_id} | Time = {scale_time}")
        if success:
            done += 1
        else:
            print(f"Scale failed: {db_id} | Error: {err}")
            failed_dbs.append(db_id)

    print("-" * 30)
    print(f"Total processed: {total}")
    print(f"Successfully scaled: {done}")
    print(f"Failed: {len(failed_dbs)}")
    print(f"Failed DB IDs: {failed_dbs}")

    # Copy results to final destination
    dest_path = f"data/database_s{scale_size}"
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)  # Clean up if it exists
    shutil.copytree("data/database/", dest_path)
