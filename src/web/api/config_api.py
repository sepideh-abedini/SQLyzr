import os
import shutil

from flask import jsonify, request
from src.util.file_utils import read_json, write_json
from src.sqlyzr.sqlyzr import Sqlyzr
from .base_api import BaseAPI
from loguru import logger

from ...configs.config_loader import ConfigData, load_config


class ConfigAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/config', methods=['GET'])(self.get_config)
        self.app.route('/api/config', methods=['POST'])(self.update_config)
        self.app.route('/api/config/cleanup', methods=['POST'])(self.cleanup)

    def get_config(self):
        data = read_json(self.config_file)
        return jsonify(data)

    def update_config(self):
        old_config = ConfigData.load(self.config_file)
        old_config = old_config.dict()
        update_data = request.json
        for key, value in update_data.items():
            old_config[key] = value
        logger.info(f"New config: {update_data}")
        write_json(self.config_file, old_config)
        try:
            sqlyzr = Sqlyzr(self.config_file)
        except Exception as e:
            print(e)
            write_json(self.config_file, old_config)
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
