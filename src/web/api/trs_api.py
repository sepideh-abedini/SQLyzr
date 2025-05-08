import os
import json
from flask import jsonify, request
from .base_api import BaseAPI
from ...sqlyzr.sqlyzr import Sqlyzr
from ...util.file_utils import read_json


class TrsAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/trs', methods=['GET'])(self.get_trs_data)

    def get_trs_data(self):
        sqlyzr = Sqlyzr(self.config_file)
        try:
            model = request.args.get('model')
            dataset = request.args.get('dataset')

            if not model or not dataset:
                return jsonify({"error": "Model and dataset parameters are required"}), 400
            trs_dir = os.path.join(sqlyzr.conf.eval_conf.base_dir, 'trs', model, dataset)

            if not os.path.exists(trs_dir):
                return jsonify({"error": f"No TRS data found for model '{model}' and dataset '{dataset}'"}), 404

            csv_files = [f for f in os.listdir(trs_dir) if f.endswith('.csv')]
            response = []
            for csv_file in csv_files:
                response.append({
                    "name": csv_file.replace('.csv', ''),
                    "stats": read_json(os.path.join(trs_dir, csv_file + ".stats.json")),
                    "repairs": read_json(os.path.join(trs_dir, csv_file + ".json"))
                })

            return jsonify(response)

        except Exception as e:
            return jsonify({"error": str(e)}), 500
