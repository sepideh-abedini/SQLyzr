import re
from datetime import datetime

log_file = "logs/all.log"

timestamps = []
utils = []

# Parse log file
with open(log_file, "r") as f:
    for line in f:
        match = re.match(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+), \d+, .+, (\d+)\s%", line.strip())
        if match:
            timestamps.append(datetime.strptime(match.group(1), "%Y/%m/%d %H:%M:%S.%f"))
            utils.append(int(match.group(2)))

# Find zero utilization intervals
intervals = []
start = None

for i, util in enumerate(utils):
    if util == 0:
        if start is None:
            start = timestamps[i]
    else:
        if start is not None:
            intervals.append((start, timestamps[i - 1]))
            start = None

# If file ends with zero utilization
if start is not None:
    intervals.append((start, timestamps[-1]))

# Print intervals and durations
for s, e in intervals:
    duration = e - s
    print(f"Zero utilization from {s} to {e} (Duration: {duration})")

print(f"START: {timestamps[0]}")
print(f"END: {timestamps[-1]}")
