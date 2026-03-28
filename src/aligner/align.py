import pandas as pd

from src.util.file_utils import read_json


class Aligner:
    def __init__(self, source_path, reference_path):
        self.source_path = source_path
        self.reference_path = reference_path
        self.verify(self.source_path)
        self.verify(self.reference_path)

    def verify(self, file_path):
        data = read_json(file_path)
        for row in data:
            assert 'cat' in row
            assert 'sub' in row

    def get_cat_dist(self, file_path):
        data = read_json(file_path)
        df = pd.DataFrame(data)
        df = df[df['cat'] != "c1000"]
        df = df[['cat']]
        counts = df['cat'].value_counts().sort_index()
        return counts

    def run(self):
        self.verify(self.source_path)
        self.verify(self.reference_path)
        src_cat_dist = self.get_cat_dist(self.source_path)
        ref_cat_dist = self.get_cat_dist(self.reference_path)

        ratios = src_cat_dist / ref_cat_dist
        print("Ratios:")
        print(ratios)

        scale_ratio = ratios.min()
        ref_scaled = scale_ratio * ref_cat_dist

        print("Scaled Ref:")
        print(ref_scaled)

        cats = ref_scaled.index.tolist()
        aligned_rows = {c: [] for c in cats}

        src_data = read_json(self.source_path)

        for row in src_data:
            cat = row['cat']
            if len(aligned_rows[cat]) < ref_scaled[cat]:
                aligned_rows[cat].append(row)

        out_rows = []
        for cat, rows in aligned_rows.items():
            print(cat, len(rows))
            out_rows.extend(rows)

        return out_rows


def main():
    aligner = Aligner('data/agg/data.test.json', 'data/sqlshare_data_release/data.json')
    aligner.run()


if __name__ == '__main__':
    main()
