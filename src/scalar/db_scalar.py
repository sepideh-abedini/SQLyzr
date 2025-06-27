import os

import pandas as pd
from sdv.metadata import Metadata
import tqdm
from sdv.multi_table import HMASynthesizer
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.utils import poc
from sdv.utils.poc import get_random_subset

from src.scalar.data_utils import read_table_from_sqlite

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
    "hr_1",
}


class DbScalar:
    def scale_db(self, db_id: str):
        if any(f.endswith("_synthetic.csv") for f in os.listdir(f"data/database/{db_id}")):
            return

        metadata = Metadata.load_from_json(f'data/database/{db_id}/meta.json')

        tables = metadata.tables.keys()

        print(f"Scaling DB: [{db_id}], tables={tables}")

        data = dict()

        for t in tqdm.tqdm(tables, total=len(tables)):
            df = read_table_from_sqlite(os.path.join("data", "database", db_id, f"{db_id}.sqlite"), t)
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

        synthetic_data = synthesizer.sample(scale=1)

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

        for t, df in merged_dfs.items():
            df.to_csv(f'data/database/{db_id}/{t}_synthetic.csv', index=False)
