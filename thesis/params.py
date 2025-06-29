import os
from pathlib import Path

# LATEST_SCORES_PATH = "all_scores_v12_aligned.csv"
# LATEST_SCORES_PATH = "scale/scores_s1.csv"
# LATEST_SCORES_PATH = "scale/scores_s10.csv"
# LATEST_SCORES_PATH = "scale/scores_s20.csv"
# LATEST_SCORES_PATH = "scale/scores_s50.csv"
# LATEST_SCORES_PATH = "scale/scores_s100.csv"
# LATEST_SCORES_PATH = "scale/scores_s1000.csv"
# LATEST_SCORES_PATH = "all_scores_v12.csv"
# LATEST_SCORES_PATH = "thesis_scores.csv"
# LATEST_SCORES_PATH = "thesis_aligned_s1.csv"
# LATEST_SCORES_PATH = "thesis_aligned_s5.csv"
# LATEST_SCORES_PATH = "thesis_scores_v2.csv"
LATEST_SCORES_PATH = "recalc/rea_new.csv"

# LATEST_SCORES_PATH = "consist_scores.csv"
OUT_DIR = "charts/unaligned"
# LATEST_SCORES_PATH = "thesis_aligned.csv"
# OUT_DIR = "charts/aligned"
os.makedirs(OUT_DIR, exist_ok=True)

# R Values
R_VALUE = 1.46
# R_SPIDER_ALL = 0
# R_SPIDER_ = 0
