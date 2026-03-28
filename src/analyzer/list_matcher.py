from src.analyzer.fix_finder import MapProp
from src.analyzer.row_matcher import match_row_prop, check_row_match


def match_lists_of_lists_full(rs1: list[list[str]], rs2: list[list[str]], rs_props: set[MapProp],
                              row_props: set[MapProp]):
    if MapProp.Injective in rs_props:
        left = rs1
        right = rs2
        reverse_row = False
    elif MapProp.Surjective in rs_props:
        left = rs2
        right = rs1
        reverse_row = True
    else:
        raise RuntimeError("The rs mapping should be either Injective or Surjective")

    if MapProp.Injective in rs_props and MapProp.Surjective in rs_props:
        if len(left) != len(right):
            return None

    nl, nr = len(left), len(right)
    candidates = dict()
    for i, row_left in enumerate(left):
        candidates_i = dict()
        for j, row_right in enumerate(right):
            if reverse_row:
                m = match_row_prop(row_right, row_left, row_props)
            else:
                m = match_row_prop(row_left, row_right, row_props)
            if m is not None:
                candidates_i[j] = m
        candidates[i] = candidates_i

    assignment = [-1] * nl
    used = [False] * nr

    def backtrack(i, m):
        if i == nl:
            return True
        for j, m_ij in candidates[i].items():
            curr_m = m
            if m:
                if reverse_row:
                    match_check = check_row_match(right[j], left[i], m, row_props)
                else:
                    match_check = check_row_match(left[i], right[j], m, row_props)
                if not match_check:
                    continue
            else:
                curr_m = m_ij

            if not used[j]:
                used[j] = True
                assignment[i] = j
                if backtrack(i + 1, curr_m):
                    return True
                used[j] = False
                assignment[i] = -1
        return False

    if backtrack(0, None):
        return {i: assignment[i] for i in range(nl)}
    return None


def match_lists_of_lists_full_mono(rs1: list[list[str]], rs2: list[list[str]], rs_props: set[MapProp],
                                   row_props: set[MapProp]):
    if MapProp.Injective in rs_props:
        left = rs1
        right = rs2
        reverse_row = False
    elif MapProp.Surjective in rs_props:
        left = rs2
        right = rs1
        reverse_row = True
    else:
        raise RuntimeError("The rs mapping should be either Injective or Surjective")

    if MapProp.Injective in rs_props and MapProp.Surjective in rs_props:
        if len(left) != len(right):
            return None

    nl, nr = len(left), len(right)
    candidates = dict()
    for i, row_left in enumerate(left):
        candidates_i = dict()
        for j, row_right in enumerate(right):
            if reverse_row:
                m = match_row_prop(row_right, row_left, row_props)
            else:
                m = match_row_prop(row_left, row_right, row_props)
            if m is not None:
                candidates_i[j] = m
        candidates[i] = candidates_i

    assignment = [-1] * nl

    def backtrack(i, m, last_j):
        if i == nl:
            return True
        for j in sorted(candidates[i].keys()):
            if j <= last_j:
                continue
            m_ij = candidates[i][j]
            curr_m = m
            if m:
                if reverse_row:
                    match_check = check_row_match(right[j], left[i], m, row_props)
                else:
                    match_check = check_row_match(left[i], right[j], m, row_props)
                if not match_check:
                    continue
            else:
                curr_m = m_ij

            assignment[i] = j
            if backtrack(i + 1, curr_m, j):
                return True
            assignment[i] = -1
        return False

    if backtrack(0, None, -1):
        return {i: assignment[i] for i in range(nl)}
    return None


def match_lists_mon_prop(rs1: list[list[str]], rs2: list[list[str]], rs_props: set[MapProp], row_props: set[MapProp]):
    mono = MapProp.Monotonic in rs_props
    if mono:
        return match_lists_of_lists_full_mono(rs1, rs2, rs_props, row_props)
    else:
        return match_lists_of_lists_full(rs1, rs2, rs_props, row_props)


def match_list_of_list_full_prop(rs1: list[list[str]], rs2: list[list[str]], rs_props: set[MapProp],
                                 row_props: set[MapProp]):
    return match_lists_mon_prop(rs1, rs2, rs_props, row_props)
