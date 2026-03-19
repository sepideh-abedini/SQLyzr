import os

from flask import jsonify, request
from src.util.file_utils import read_json, write_json
from src.sqlyzr.sqlyzr import Sqlyzr
from .base_api import BaseAPI
from loguru import logger

from ...configs.config_loader import ConfigData


class ConfigAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/config', methods=['GET'])(self.get_config)
        self.app.route('/api/config', methods=['POST'])(self.update_config)

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

