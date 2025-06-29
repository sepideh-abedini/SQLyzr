import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re

log_file = "logs/all.log"

timestamps = []
utilizations = []

with open(log_file, "r") as f:
    for line in f:
        # Match timestamp and utilization
        match = re.match(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+), \d+, .+, (\d+)\s%", line.strip())
        if match:
            timestamps.append(match.group(1))
            utilizations.append(int(match.group(2)))

# Create DataFrame
df = pd.DataFrame({
    "timestamp": pd.to_datetime(timestamps),
    "utilization": utilizations
})

df["elapsed_seconds"] = range(len(df))
count_non_zero = (df["utilization"] > 0).sum()
print(f"Number of rows where utilization > 0: {count_non_zero}")
print(len(df))

# Plot
sns.set(style="whitegrid")
fig = plt.figure(figsize=(10, 5))
sns.lineplot(x="elapsed_seconds", y="utilization", data=df)

plt.title("GPU Utilization (1x H100 80GB)")
plt.xlabel("Elapsed Time (seconds)")
plt.ylabel("Utilization (%)")
plt.ylim(0, 100)
plt.tight_layout()
plt.show()

fig.savefig("util_chart.png")
