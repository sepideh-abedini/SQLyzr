from flask import jsonify, request

from experimental.query_runner import calculate_R
from .base_api import BaseAPI
from ...configs.config_loader import load_config


class UtilsAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/utils/calcr', methods=['POST'])(self.calculate_r)

    async def calculate_r(self):
        try:
            req = request.json
            if not req:
                return jsonify({"error": "No JSON data provided"}), 400

            p = int(req.get('p'))
            k = int(req.get('k'))

            conf = load_config(self.config_file)

            result = await calculate_R(conf.eval_conf.dataset_configs, k, p)

            return jsonify({
                "result": result,
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500
