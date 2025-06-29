import sys

from src.chart.charter import draw_all_charts


def main(input, output_dir):
    draw_all_charts(input, output_dir, [
        "Overall",
        # "Execution Accuracy",
        # "Relaxed Execution Accuracy",
        # "Exact Match",
        # "Execution Time",
        # "Token Usage",
        # "Execution Time Consistency",
        # "Execution Time Inconsistency",
        # "Complexity Consistency",
        # "Complexity Inconsistency",
        # "Category Distribution",
    ])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
