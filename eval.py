import argparse

import matplotlib.pyplot as plt
from pandas import Series

from src.evaluator.din_evaluator import DinResultEvaluator
from src.evaluator.din_preprocessor import DinResultPreProcessor

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type=str)
parser.add_argument("-o", "--output", type=str)
parser.add_argument("-d", "--db", type=str)
args = parser.parse_args()


def draw_pie_chart(series: Series):
    plt.pie(series.values, labels=series.index, autopct='%1.1f%%', startangle=140)
    plt.title("Category of gold SQL where pred is wrong")
    plt.show()


def main():

    pred_file_path = 'out/pred.csv'
    # pre_processor = DinResultPreProcessor(in_path=args.input, out_path=pred_file_path)
    # pre_processor.process()

    evaluator = DinResultEvaluator(in_path=pred_file_path, out_path=args.output, dbs_dir=args.db)
    df = evaluator.process()

if __name__ == '__main__':
    main()
