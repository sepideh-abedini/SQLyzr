from flask import jsonify
from .base_api import BaseAPI


class ModelsAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/models', methods=['GET'])(self.get_models)
        self.app.route('/api/datasets', methods=['GET'])(self.get_datasets)

    def get_models(self):
        try:
            from src.eval.single_run_config import ModelName
            models = ["din", "dail", "dum"]
            return jsonify({"models": models})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_datasets(self):
        try:
            from src.configs.datasets import DatasetName
            datasets = ["spider", "bird", "beaver", "agg"]
            return jsonify({"datasets": datasets})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
