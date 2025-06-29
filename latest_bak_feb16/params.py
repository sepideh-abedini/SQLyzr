import os
from pathlib import Path

# LATEST_SCORES_PATH = "all_scores_v12_aligned.csv"
# LATEST_SCORES_PATH = "spider_scale/scores_s100.csv"
# LATEST_SCORES_PATH = "all_scores_v12.csv"
LATEST_SCORES_PATH = "aligned/aligned.csv"

OUT_DIR = Path(LATEST_SCORES_PATH).stem
os.makedirs(OUT_DIR, exist_ok=True)
