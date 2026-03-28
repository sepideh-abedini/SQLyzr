import shutil

from flask import jsonify, request
from loguru import logger

from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.file_utils import read_json, write_json
from .base_api import BaseAPI
from ...configs.config_loader import ConfigData, load_config


class ConfigAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/config', methods=['GET'])(self.get_config)
        self.app.route('/api/config', methods=['POST'])(self.update_config)
        self.app.route('/api/config/cleanup', methods=['POST'])(self.cleanup)
        self.app.route('/api/config/reset', methods=['POST'])(self.reset_config)

    def get_config(self):
        data = read_json(self.config_file)
        if 1 in data['scales']:
            data['scales'].remove(1)
        return jsonify(data)

    def reset_config(self):
        orig_conf_file = self.config_file.replace(".json", ".orig.json")
        shutil.copy(orig_conf_file, self.config_file)
        return jsonify({"message": "Configuration file reset to original!"})

    def update_config(self):
        with BaseAPI._lock:
            try:
                old_config = ConfigData.load(self.config_file)
                old_config = old_config.dict()
            except Exception as e:
                old_config = dict()
            update_data = request.json
            logger.info(f"Updating: {update_data}")
            if 1 not in update_data['scales']:
                update_data['scales'] = [1] + update_data['scales']
            for key, value in update_data.items():
                old_config[key] = value
            logger.info(f"New config: {update_data}")
            write_json(self.config_file, old_config)
            try:
                conf_data = ConfigData.load(self.config_file)
                sqlyzr = Sqlyzr(self.config_file)
                conf_data.save(self.config_file)
            except Exception as e:
                conf_data_raw = read_json(self.config_file)
                write_json(self.config_file, old_config)
                logger.error(f"Update failed! {e}")
                return str(e), 400
            return jsonify({"message": "Configuration updated successfully"})

    def cleanup(self):
        conf = load_config(self.config_file)
        conf_data = ConfigData.load(self.config_file)
        conf_data = conf_data.model_copy(update={
            "dataset_versions": [conf_data.dataset_versions[0]]
        })
        conf_data.save(self.config_file)
        out_dir = conf_data.get_model_dataset_dir()
        logger.info(f"Deleting: {out_dir}")
        shutil.rmtree(out_dir)
        return jsonify({"message": "Cleanup done!"})
