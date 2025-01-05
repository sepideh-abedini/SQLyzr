from dataclasses import dataclass
from typing import Dict


@dataclass
class ModelRunStats:
    total_pred_seconds: int = 0
