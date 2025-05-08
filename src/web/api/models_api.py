from flask import jsonify
from .base_api import BaseAPI
from ...sqlyzr.sqlyzr import Sqlyzr


class ModelsAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/models', methods=['GET'])(self.get_models)
        self.app.route('/api/datasets', methods=['GET'])(self.get_datasets)

    def get_models(self):
        sqlyzr = Sqlyzr(self.config_file)
        return jsonify({"models": list(sqlyzr.conf.eval_conf.models)})

    def get_datasets(self):
        sqlyzr = Sqlyzr(self.config_file)
        return jsonify({"datasets": list(sqlyzr.conf.eval_conf.datasets)})
