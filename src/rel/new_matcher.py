from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class Row:
    vals: list[str]


@dataclass
class Result:
    rows: list[Row]


l1 = [
    ["a"],
    ["a", "b"],
]

l2 = [
    ["a", "b"],
    ["a"],
]


def match(l1: list[str], l2: list[str]):
    val_to_idx_2 = defaultdict(list)
    for i, v2 in enumerate(l2):
        val_to_idx_2[v2].append(i)

    matching = dict()
    for i, v1 in enumerate(l1):
        if v1 not in val_to_idx_2:
            return None
        ids = val_to_idx_2[v1]
        if len(ids) == 0:
            return None
        matching[i] = val_to_idx_2[v1].pop()
    assert len(matching) == len(l1)
    return matching


def max_matching_dfs(L1, L2):
    n1, n2 = len(L1), len(L2)
    graph = [[] for _ in range(n1)]
    for i, l1 in enumerate(L1):
        for j, l2 in enumerate(L2):
            if match(l1, l2) is not None:
                graph[i].append(j)

    pair_right = [-1] * n2

    def dfs(u, visited):
        for v in graph[u]:
            if not visited[v]:
                visited[v] = True
                if pair_right[v] == -1 or dfs(pair_right[v], visited):
                    pair_right[v] = u
                    return True
        return False

    for u in range(n1):
        visited = [False] * n2
        if not dfs(u, visited):
            return None

    return {pair_right[v]: v for v in range(n2) if pair_right[v] != -1}


print(max_matching_dfs(l1, l2))
