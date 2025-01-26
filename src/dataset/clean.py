from src.configs.dataset import SPIDER_DEV
from src.sqlyzr.validate import validate_dataset


def main():
    validate_dataset(config, f"{SPIDER_DEV.get_data_path()}.clean.json")


if __name__ == '__main__':
    main()
