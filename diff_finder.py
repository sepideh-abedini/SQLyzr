

def read_file(filename):
    with open(filename, 'r') as file:
        return set(file.read().splitlines())

def compare_files(file1, file2):
    lines_file1 = read_file(file1)
    lines_file2 = read_file(file2)

    unique_to_file1 = lines_file1 - lines_file2
    unique_to_file2 = lines_file2 - lines_file1

    return unique_to_file1, unique_to_file2

def main():
    path = "data/datasets/spider/"

    file1_path = path + "s_matched_lines.txt"  # 774
    file2_path = path + "spider_matched_lines.txt"  # 721
    output_path = path + "unique_in_gold.txt"

    with open(file1_path, 'r') as f1:
        file1_lines = f1.readlines()

    with open(file2_path, 'r') as f2:
        file2_lines = f2.readlines()
    #

    set1 = set()
    for line in file1_lines:
        val = int(line.strip())
        set1.add(val)

    set2 = set()
    for line in file2_lines:
        val = int(line.strip())
        set2.add(val)


    diff_lines = set1.symmetric_difference(set2)

    print("____dif_lines____:", diff_lines)
    print("len", len(diff_lines))
#
# with open(output_path, 'w') as diff_file:
#     for line in diff_lines:
#         diff_file.write(line)
#     unique_to_file1, unique_to_file2 = compare_files(file1_path, file2_path)
#
#     print("Lines unique to File1:")
#     for line in unique_to_file1:
#         print(line)
#
#     print("\nLines unique to File2:")
#     for line in unique_to_file2:
#         print(line)


if __name__ == "__main__":
    main()

