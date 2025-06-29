import pandas as pd
import tqdm

from thesis.align_sqlshare import align_sqlyzr

NUM_SAMPLES = 5
dfs = [align_sqlyzr() for _ in tqdm.tqdm(range(NUM_SAMPLES))]
combined_df = pd.concat(dfs, ignore_index=True)

combined_df.to_csv("thesis_aligned.csv")

print(f"Final shape: {combined_df.shape}")
