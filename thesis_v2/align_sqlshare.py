import pandas as pd

THESIS_SCORES = "thesis_scores.csv"


def sqlyzr_uniq_questions(file_path):
    df = pd.read_csv(file_path)
    df['ds_idx'] = df['dst'].astype(str) + df['ds_idx'].astype(str)
    df = df.groupby(['ds_idx'], as_index=False).first()
    return df


def process_sqlyzr(file_path):
    df = sqlyzr_uniq_questions(file_path)
    df = df[['cat']]
    counts = df['cat'].value_counts().sort_index()
    return counts


def print_cat_dist(cat_file):
    df = pd.read_csv(cat_file)
    df = df[df['cat'] != "c1000"]
    df = df[['cat']]
    counts = df['cat'].value_counts().sort_index()
    return counts


def align_sqlyzr():
    counts_sqlshare = print_cat_dist("align/sqlshare_cats.csv")
    counts_sqlyzr = process_sqlyzr(THESIS_SCORES)

    df = pd.read_csv(THESIS_SCORES)

    print("SQLyzr Total:", df.shape[0])
    print("SQLyzr Questions:", counts_sqlyzr.sum())
    print("SQLShare Questions:", counts_sqlshare.sum())

    ratios = counts_sqlyzr / counts_sqlshare
    print("Ratios:")
    print(ratios)

    scale_ratio = ratios.min()
    sqlshare_scaled = scale_ratio * counts_sqlshare
    print("SQLShare Scaled:")
    print(sqlshare_scaled)
    print("SQLyzr Counts:")
    print(counts_sqlyzr)
    print("SQLShare Counts:")
    print(counts_sqlshare)

    cats = sqlshare_scaled.index.tolist()
    aligned_rows = {c: set() for c in cats}

    sqlyzr_questions = sqlyzr_uniq_questions(THESIS_SCORES)
    sqlyzr_questions = sqlyzr_questions.sample(frac=1).reset_index(drop=True)

    for index, row in sqlyzr_questions.iterrows():
        cat = row['cat']
        if len(aligned_rows[cat]) < sqlshare_scaled[cat]:
            aligned_rows[cat].add(str(row['ds_idx']))

    for cat, rows in aligned_rows.items():
        print(cat, len(rows))

    aligned_ids = set().union(*aligned_rows.values())
    print(len(aligned_ids))

    df['ds_idx'] = df['dst'].astype(str) + df['ds_idx'].astype(str)

    aligned_rows = []
    for index, row in df.iterrows():
        cat = row['cat']
        idx = row['ds_idx']
        if row['ds_idx'] in aligned_ids:
            aligned_rows.append(row)

    print(len(aligned_rows))
    aligned_df = pd.DataFrame.from_records(aligned_rows)
    return aligned_df
