import numpy as np
import pandas as pd

SCORES_PATH = "data/all.fake.csv"

datasets = ['spider', 'bird', 'beaver']
models = ['din', 'dail']

rand_score = lambda: np.random.randint(0, 2)
df = pd.DataFrame([(d, m, rand_score, rand_score, rand_score, rand_score) for d in datasets for m in models],
                  columns=["dataset", "model", "ea", "rea", "em", "cc"])
