import re

max_mem = 0.0

with open("util.log") as f:
    for line in f:
        match = re.search(r"Memory Usage:\s+([\d.]+)\s+MB", line)
        if match:
            mem = float(match.group(1))
            max_mem = max(max_mem, mem)

print(max_mem)
