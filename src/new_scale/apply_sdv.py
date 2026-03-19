import os
import shutil

from src.eval.dataset_config import DatasetConfig
from src.new_scale.insert import insert_synthetic_data, backup_and_revert
from src.new_scale.scale_3 import scale_db
from src.new_scale.table_meta import save_meta


def copy_scaled_db(ds_conf: DatasetConfig, db_id: str, scale: int):
    scaled_dir = f"{ds_conf.get_db_path()}_{scale}"
    os.makedirs(scaled_dir, exist_ok=True)
    orig_db_dir = os.path.join(ds_conf.get_db_path(), db_id)
    shutil.copytree(orig_db_dir, os.path.join(scaled_dir, db_id), dirs_exist_ok=True)
    orig_db_file = ds_conf.get_db_file_path(db_id)
    backup_and_revert(orig_db_file)
    return scaled_dir


def apply_scaling(ds_conf: DatasetConfig, db_id: str, scale: int):
    save_meta(ds_conf.get_db_path(), db_id)
    scale_db(ds_conf.get_db_path(), db_id, scale)
    insert_synthetic_data(ds_conf.get_db_path(), db_id)
    scaled_dir = copy_scaled_db(ds_conf, db_id, scale)
    return scaled_dir

