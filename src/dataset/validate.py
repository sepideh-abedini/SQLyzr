import json

from tqdm import tqdm

from src.cat.catter import Catter
from src.eval.dataset_config import DatasetConfig
from src.dataset.models import SpiderExample


def validate_dataset(conf: DatasetConfig):
    catter = Catter()
    errors = []
    total = 0
    with open(conf.get_data_path()) as file:
        data = json.load(file)
        for i, entry in tqdm(enumerate(data), total=len(data), desc=f"Validating dataset: {conf.dataset_dir}"):
            example = SpiderExample.model_validate(entry)
            cat = catter.get_category(example.query)
            total += 1
            if cat is None:
                errors.append((i, example.query))

    print(f"Num dataset errors: {len(errors)}/{total}")
    with open(f"{conf.get_data_path()}.err", "w") as errors_file:
        for error in errors:
            errors_file.write(f"{error}\n")
    if len(errors) > 0:
        print("Invalid SQLs found!")
    else:
        print("Dataset is valid!")
