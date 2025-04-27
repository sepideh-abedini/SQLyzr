import re

from src.util.str_utils import shrink_whitespaces

data_dir = 'data/sqlshare_data_release/'
with open(data_dir + "queries.txt", 'r') as f:
    lines = f.readlines()

non_comment_lines = [line for line in lines if not line.lstrip().startswith('--')]

cleaned = []
for line in non_comment_lines:
    pat = "(.*)--(.*)$"
    if re.search(pat, line):
        cleaned_line = re.sub(pat, r'\1', line)
    else:
        cleaned_line = line
    cleaned_line = shrink_whitespaces(cleaned_line)
    cleaned.append(cleaned_line)

with open(data_dir + "queries.non_comment.txt", 'w') as f:
    f.write("\n".join(cleaned))
