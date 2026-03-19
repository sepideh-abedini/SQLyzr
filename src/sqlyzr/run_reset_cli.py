import argparse
import asyncio

from src.chart.charter import draw_all_charts
from src.configs.config_loader import ConfigData, load_config


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    conf = load_config(args.config)
    conf_data = ConfigData.load(args.config)
    conf_data = conf_data.model_copy(update={
        "dataset_versions": [conf_data.dataset_versions[0]]
    })
    conf_data.save(args.config)
    draw_all_charts(conf.eval_conf.get_raw_scores_path(),
                    out_dir=conf.eval_conf.charts_dir,
                    included_charts=["Category Distribution"],
                    hue="dst_ver")


if __name__ == "__main__":
    asyncio.run(main())
