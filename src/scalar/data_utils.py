import sqlite3

import pandas as pd


def drop_invalid_numeric_rows(df):
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if not numeric_cols:
        return df
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=numeric_cols, how='any')
    return df
    # valid_mask = ~df[numeric_cols].isna().any(axis=1) & ~np.isinf(df[numeric_cols]).any(axis=1)
    # return df[valid_mask].copy()


def read_table_from_sqlite(db_path, table_name, k=None):
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda b: b.decode(errors='replace')

    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)

    df.columns = df.columns.str.lower()

    result = conn.execute(f"PRAGMA table_info({table_name})")
    columns_info = result.fetchall()
    conn.close()

    for col_info in columns_info:
        col_name = col_info[1]
        col_type = col_info[2].upper()

        if col_name in df.columns:
            if col_type in ('INTEGER', 'INT'):
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                df = df.dropna(subset=[col_name])
                df[col_name] = df[col_name].astype('int')
            elif col_type in ('REAL', 'FLOAT', 'DOUBLE', 'NUMERIC'):
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                df = df.dropna(subset=[col_name])
                df[col_name] = df[col_name].astype('float')

    non_numeric_cols = df.select_dtypes(exclude='number').columns.tolist()
    for col in non_numeric_cols:
        numeric_series = pd.to_numeric(df[col], errors='coerce')
        if not numeric_series.isna().any():
            if all(numeric_series == numeric_series.astype(int)):
                df[col] = numeric_series.astype(int)
            else:
                df[col] = numeric_series.astype(float)

    df = drop_invalid_numeric_rows(df)

    return df
