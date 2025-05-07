import os
import json
from flask import jsonify, request
from .base_api import BaseAPI

class TrsAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/trs', methods=['GET'])(self.get_trs_data)
    
    def get_trs_data(self):
        try:
            model = request.args.get('model')
            dataset = request.args.get('dataset')
            
            if not model or not dataset:
                return jsonify({"error": "Model and dataset parameters are required"}), 400
            
            trs_dir = os.path.join('out', 'dail-din_agg_small', 'trs', model, dataset)
            
            if not os.path.exists(trs_dir):
                return jsonify({"error": f"No TRS data found for model '{model}' and dataset '{dataset}'"}), 404
            
            json_files = [f for f in os.listdir(trs_dir) if f.endswith('.json')]
            
            if not json_files:
                return jsonify({"error": f"No JSON files found in TRS directory for model '{model}' and dataset '{dataset}'"}), 404
            
            json_file_path = os.path.join(trs_dir, json_files[0])
            
            with open(json_file_path, 'r') as f:
                trs_data = json.load(f)
            
            return jsonify({"trs_data": trs_data})
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500