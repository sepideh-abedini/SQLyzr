import os
from pathlib import Path

# LATEST_SCORES_PATH = "all_scores_v12_aligned.csv"
# LATEST_SCORES_PATH = "spider_scale/scores_s100.csv"
# LATEST_SCORES_PATH = "all_scores_v12.csv"
# LATEST_SCORES_PATH = "thesis_scores.csv"
# LATEST_SCORES_PATH = "thesis_aligned_1.csv"
# LATEST_SCORES_PATH = "thesis_aligned_10.csv"
LATEST_SCORES_PATH = "thesis_aligned_5.csv"
# LATEST_SCORES_PATH = "thesis_aligned_100.csv"

# OUT_DIR = "charts/unaligned"
OUT_DIR = "charts/align"
os.makedirs(OUT_DIR, exist_ok=True)
