import re
from enum import Enum
from difflib import SequenceMatcher
from typing import Optional

from loguru import logger


def delete_whitespace(content):
    content = content.replace('\n', '').replace('\r', '')
    return content


def is_quoted(s) -> bool:
    return (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'"))


def quote_str(s) -> str:
    if is_quoted(s):
        return s
    else:
        return f"'{s}'"


def shrink_whitespaces(s: Optional[str]) -> Optional[str]:
    if s is None:
        return s
    s = s.strip()
    s = s.replace('\n', ' ').replace('\r', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s


def pascal_to_snake(name: str) -> str:
    """Example: 'BarBaz' -> 'bar_baz'"""
    snake_case = re.sub('([A-Z])', r'_\1', name).lower()
    return snake_case.lstrip('_')


def split_pascal(name: str) -> str:
    """Example: 'BarBaz' -> 'Bar Baz'"""
    return " ".join(re.findall(r'[A-Z][a-z]*|[a-z]+|[A-Z]+(?=[A-Z]|$)', name))


def split_to_snake(space_separated_str: str) -> str:
    """Example: 'Bar Baz' -> 'bar_baz'"""
    return '_'.join(space_separated_str.lower().split())


class Color(Enum):
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def colored(s: str, color: Color):
    return f"{color.value}{s}{Color.ENDC.value}"


def get_colored_diff(a: str, b: str) -> str:
    a = a.lower()
    b = b.lower()
    matcher = SequenceMatcher(a=a, b=b, isjunk=lambda c: c in " \t")
    result = ""
    for op_code in matcher.get_opcodes():
        (tag, i1, i2, j1, j2) = op_code
        if tag == 'equal':
            result += a[i1:i2]
        if tag == 'insert':
            result += colored(b[j1:j2], Color.GREEN)
        if tag == 'delete':
            result += colored(a[i1:i2], Color.RED)
        if tag == 'replace':
            result += colored(b[j1:j2], Color.BLUE)
    return result


def extract_sql(output):
    # output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL)
    output = output.strip()
    output = output.strip("\"")
    sql = "SELECT"
    if output.startswith("SELECT"):
        sql = output
    elif "```sql" in output:
        res = re.findall(r"```sql([\s\S]*?)```", output)
        if len(res) > 0:
            sql = res[0]
    elif "```" in output:
        res = re.findall(r"```([\s\S]*?)```", output)
        if len(res) > 0:
            sql = res[0]
    elif "`" in output:
        res = re.findall(r"`([\s\S]*?)`", output)
        if len(res) > 0:
            sql = res[0]
    else:
        logger.error(f"Failed to extract sql from output: {output}")
    sql = sql.strip()
    sql = sql.replace("\n", " ")
    return sql


def bump_ver_str(ver: str) -> str:
    assert ver.startswith("v")
    ver_num = int(ver.replace("v", ""))
    new_ver_num = ver_num + 1
    new_ver = f"v{new_ver_num}"
    return new_ver


def bump_ver(file_path):
    ver = file_path.rsplit(".")[-2]
    new_ver = bump_ver_str(ver)
    new_path = file_path.replace(ver, new_ver)
    return new_path
