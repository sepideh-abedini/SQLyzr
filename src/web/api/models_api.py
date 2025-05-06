from flask import jsonify
from .base_api import BaseAPI

class ModelsAPI(BaseAPI):
    """API for model and dataset-related endpoints"""
    
    def register_routes(self):
        """Register model and dataset-related routes with the Flask application"""
        self.app.route('/api/models', methods=['GET'])(self.get_models)
        self.app.route('/api/datasets', methods=['GET'])(self.get_datasets)
    
    def get_models(self):
        """Get the list of available models"""
        try:
            from src.eval.single_run_config import ModelName
            models = ["din", "dail", "dum"]
            return jsonify({"models": models})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_datasets(self):
        """Get the list of available datasets"""
        try:
            from src.configs.datasets import DatasetName
            datasets = ["spider", "bird", "beaver", "agg"]
            return jsonify({"datasets": datasets})
        except Exception as e:
            return jsonify({"error": str(e)}), 500