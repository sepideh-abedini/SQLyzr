def flatten(lst):
    flat = [item for sublist in lst for item in sublist]
    return flat


def chunk_list(lst, k):
    size = len(lst) // k + (len(lst) % k > 0)
    return [lst[i:i + size] for i in range(0, len(lst), size)]
