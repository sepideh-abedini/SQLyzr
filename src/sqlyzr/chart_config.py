from typing import List, Literal

from openai import BaseModel

ChartName = Literal[
    "Execution Accuracy",
    "Relaxed Execution Accuracy",
    "Exact Match",
    "Execution Time",
    "Token Usage",
    "Execution Time Consistency",
    "Execution Time Inconsistency",
    "Complexity Consistency",
    "Complexity Inconsistency"
]


