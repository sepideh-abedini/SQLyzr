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


def match_lists_of_lists(L1: list[list[str]], L2: list[list[str]]):
    used = [False] * len(L2)
    result = {}

    for i, l1 in enumerate(L1):
        found = False
        for j, l2 in enumerate(L2):
            if not used[j] and match(l1, l2) is not None:
                result[i] = j
                used[j] = True
                found = True
                break
        if not found:
            return None

    return result


def match_lists_of_lists_full(L1: list[list[str]], L2: list[list[str]]):
    n1, n2 = len(L1), len(L2)
    candidates = [[j for j, l2 in enumerate(L2) if match(l1, l2) is not None] for l1 in L1]
    assignment = [-1] * n1
    used = [False] * n2

    def backtrack(i):
        if i == n1:
            return True
        for j in candidates[i]:
            if not used[j]:
                used[j] = True
                assignment[i] = j
                if backtrack(i + 1):
                    return True
                used[j] = False
                assignment[i] = -1
        return False

    if backtrack(0):
        return {i: assignment[i] for i in range(n1)}
    return None


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


print(match_lists_of_lists(l1, l2))
print(match_lists_of_lists_full(l1, l2))
print(max_matching_dfs(l1, l2))
