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
        csv_files = []
        for run_conf in sqlyzr.conf.eval_conf.get_run_confs():
            trs_path = run_conf.get_trs_path()
            csv_files.append(trs_path)

        try:
            response = []
            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    response.append({
                        "name": csv_file.replace('.csv', ''),
                        "stats": read_json(csv_file + ".stats.json"),
                        "repairs": read_json(csv_file + ".json")
                    })

            return jsonify(response)

        except Exception as e:
            return jsonify({"error": str(e)}), 500
