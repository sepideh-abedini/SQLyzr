def get_num_lines(file_path: str):
    with open(file_path) as f:
        return len(f.readlines())
