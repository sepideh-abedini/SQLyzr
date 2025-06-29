import argparse

import pandas as pd
from natsort import natsorted


def prepare_csv(merged_df):
    csv_df = pd.DataFrame(index=merged_df.index)

    for col in merged_df.columns:
        csv_df[f"{col} #"] = merged_df[col]
        csv_df[f"{col} %"] = (merged_df[col] / merged_df[col].sum() * 100).round(2)

    # Example for Aligned SQLLyzr x5
    if 'aligned' in merged_df.columns:
        csv_df['Aligned SQLLyzr x5 #'] = (merged_df['aligned'] * 5).astype(int)
        csv_df['Aligned SQLLyzr x5 %'] = (
                csv_df['Aligned SQLLyzr x5 #'] / csv_df['Aligned SQLLyzr x5 #'].sum() * 100).round(2)

    # Add Total row
    total_row = pd.DataFrame(csv_df.sum()).T
    total_row.index = ['Total']
    csv_df = pd.concat([csv_df, total_row])

    return csv_df


def main(in_file, aligned_file, sqlshare_file, out_file):
    sqlyzr = pd.read_csv(in_file)
    sqlyzr = sqlyzr[(sqlyzr['tmp'] == 0.2) & (sqlyzr['itr'] == 0) & (sqlyzr['model'] == 'din')]
    aligned = pd.read_csv(aligned_file)
    aligned = aligned[(aligned['tmp'] == 0.2) & (aligned['itr'] == 0) & (aligned['model'] == 'din')]
    sqlshare = pd.read_csv(sqlshare_file)

    def print_cat_dist(df, name):
        df = df[df['cat'] != "c1000"]
        print(f"{name} Count")
        print(df["cat"].value_counts(normalize=False))
        print(f"{name} Percentage")
        print(df["cat"].value_counts(normalize=True))

    print_cat_dist(sqlyzr, "sqlyzr")
    print_cat_dist(sqlshare, "sqlshare")
    print_cat_dist(aligned, "aligned")

    # Count categories for each dataset
    def cat_counts(df):
        df = df[df['cat'] != "c1000"]
        return df['cat'].value_counts().sort_index()

    merged_df = pd.DataFrame({
        'sqlyzr': cat_counts(sqlyzr),
        'sqlshare': cat_counts(sqlshare),
        'aligned': cat_counts(aligned),
    }).fillna(0).astype(int)

    csv_df = prepare_csv(merged_df)
    csv_df.to_csv(out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-a", required=True)
    parser.add_argument("-s", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.a, args.s, args.o)
