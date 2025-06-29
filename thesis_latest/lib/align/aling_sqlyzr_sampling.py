import argparse

import pandas as pd
import tqdm

from thesis_latest.lib.align.align_sqlyzr import align_sqlyzr

NUM_SAMPLES = 5


def main(input_file, sqlshare_file, output_file):
    dfs = [align_sqlyzr(input_file, sqlshare_file) for _ in tqdm.tqdm(range(NUM_SAMPLES))]
    combined_df = pd.concat(dfs, ignore_index=True)

    combined_df.to_csv(output_file)

    print(f"Final shape: {combined_df.shape}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-s", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.s, args.o)
