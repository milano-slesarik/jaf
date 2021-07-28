def file_lines_count(filepath: str):
    with open(filepath) as f:
        count = 0
        for _ in f:
            count += 1
    return count
