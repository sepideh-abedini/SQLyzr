import os
import json
import asyncio
import platform

import multiprocessing as mp
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from src.sqlyzr.sqlyzr import Sqlyzr
from src.configs.config_loader import ConfigData
from src.util.file_utils import read_json, write_json
from src.util.log_util import configure_logging

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "gui.json"


@app.route('/api/config', methods=['GET'])
def get_config():
    data = read_json(CONFIG_FILE)
    return jsonify(data)


@app.route('/api/config', methods=['POST'])
def update_config():
    config = request.json
    write_json(CONFIG_FILE, config)
    return jsonify({"message": "Configuration updated successfully"})


@app.route('/api/run', methods=['POST'])
async def run_sqlyzr():
    sqlyzr = Sqlyzr(CONFIG_FILE)
    try:
        await sqlyzr.run()
        return jsonify({
            "message": "SQLyzr executed successfully",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/results', methods=['GET'])
def get_results():
    try:
        sqlyzr = Sqlyzr(CONFIG_FILE)
        results_path = sqlyzr.conf.eval_conf.get_scores_path()

        if os.path.exists(results_path):
            # Read CSV file using pandas
            df = pd.read_csv(results_path)

            # Convert to dictionary format for DataTables
            data = {
                "headers": df.columns.tolist(),
                "rows": df.values.tolist()
            }

            # Also include the raw CSV for backward compatibility
            with open(results_path, 'r') as f:
                raw_results = f.read()

            return jsonify({
                "results": raw_results,
                "data": data
            })
        else:
            return jsonify({
                "error": "No results file found"
            }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def serve_ui():
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/vue'), 'index.html')


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    vue_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/vue')
    vue_file = os.path.join(vue_dir, path)

    if os.path.exists(vue_file) and os.path.isfile(vue_file):
        return send_from_directory(vue_dir, path)

    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    static_file = os.path.join(static_dir, path)

    if os.path.exists(static_file) and os.path.isfile(static_file):
        return send_from_directory(static_dir, path)

    return send_from_directory(vue_dir, 'index.html')


if __name__ == '__main__':
    configure_logging()
    if platform.system() == "Linux":
        mp.set_start_method("spawn", force=True)
    app.run(debug=True, host='0.0.0.0', port=7777)
