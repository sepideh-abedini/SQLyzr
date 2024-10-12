from src.util.str_utils import get_colored_diff

a = "select max(capacity), average from stadium"
b = "SELECT MAX(Capacity), AVG(Capacity) FROM stadium"

diff = get_colored_diff(a, b)
print(a)
print(b)
print(diff)
