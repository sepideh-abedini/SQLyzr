from src.configs.sqlyzr import DIN_SPIDER_DEV
from src.sqlyzr.validate import validate_dataset


def main():
    config = DIN_SPIDER_DEV
    validate_dataset(config, f"{config.eval_conf.dataset_config.get_data_path()}.clean.json")


if __name__ == '__main__':
    main()
