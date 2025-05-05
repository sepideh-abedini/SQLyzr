import logging
import multiprocessing as mp
import os
import platform

import pandas as pd
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

from src.sqlyzr.pipeline_config import SQLYZR_PIPELINE_STATUS_PATH
from src.sqlyzr.sqlyzr_lock import SQLYZR_LOCK_PATH, SqlyzrLock

logging.basicConfig(level=logging.DEBUG)

from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.file_utils import read_json, write_json
from src.util.log_util import configure_logging

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "gui.json"


@app.route('/api/log', methods=['GET'])
def get_logs():
    try:
        log_file_path = "info.log"
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                logs = f.read()
            return jsonify({"logs": logs})
        else:
            return jsonify({"error": "Log file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    data = read_json(CONFIG_FILE)
    return jsonify(data)


@app.route('/api/config', methods=['POST'])
def update_config():
    old_config = read_json(CONFIG_FILE)
    config = request.json
    write_json(CONFIG_FILE, config)
    try:
        sqlyzr = Sqlyzr(CONFIG_FILE)
    except Exception as e:
        write_json(CONFIG_FILE, old_config)
        return jsonify({"Invalid Config!": str(e)}), 400
    return jsonify({"message": "Configuration updated successfully"})


@app.route('/api/run', methods=['POST'])
async def run_sqlyzr():
    logging.info("Running SQlyzr")
    sqlyzr = Sqlyzr(CONFIG_FILE)
    try:
        logging.info("Starting SQlyzr")
        await sqlyzr.run()
        return jsonify({
            "message": "SQLyzr executed successfully",
        })
    except Exception as e:
        logging.error("ERROR Running SQlyzr")
        logging.error(e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/run/status', methods=['GET'])
def get_run_status():
    is_running = os.path.exists(SQLYZR_LOCK_PATH)
    return jsonify({"is_running": is_running})


@app.route('/api/pipeline/status', methods=['GET'])
def get_pipeline_status():
    if os.path.exists(SQLYZR_PIPELINE_STATUS_PATH):
        data = read_json(SQLYZR_PIPELINE_STATUS_PATH)
    else:
        data = {}
    return jsonify(data)


@app.route('/api/results', methods=['GET'])
def get_results():
    try:
        sqlyzr = Sqlyzr(CONFIG_FILE)
        results_path = sqlyzr.conf.eval_conf.get_scores_path()

        if os.path.exists(results_path):
            df = pd.read_csv(results_path)
            data = {
                "headers": df.columns.tolist(),
                "rows": df.values.tolist()
            }
            return jsonify({
                "data": data
            })
        else:
            return jsonify({
                "error": "No results file found"
            }), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/charts', methods=['GET'])
def get_charts():
    try:
        sqlyzr = Sqlyzr(CONFIG_FILE)
        files = [os.path.basename(f) for f in os.listdir(sqlyzr.conf.eval_conf.charts_dir)]
        return jsonify({
            "charts": files,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/charts/<chart_name>', methods=['GET'])
def get_chart(chart_name):
    try:

        sqlyzr = Sqlyzr(CONFIG_FILE)
        full_path = os.path.join(sqlyzr.conf.eval_conf.charts_dir, chart_name)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            full_path = "../../" + full_path
            return send_file(full_path)
        else:
            return jsonify({"error": f"Chart '{chart_name}' not found"}), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/models', methods=['GET'])
def get_models():
    try:
        from src.eval.single_run_config import ModelName
        models = ["din", "dail", "dum"]
        return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    try:
        from src.configs.datasets import DatasetName
        datasets = ["spider", "bird", "beaver", "agg"]
        return jsonify({"datasets": datasets})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/trs', methods=['GET'])
def get_trs_file():
    pass


def count_lines(filename):
    with open(filename, 'rb') as f:
        return sum(1 for _ in f)


@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        path = request.args.get('path', '')
        sqlyzr = Sqlyzr(CONFIG_FILE)
        base_dir = sqlyzr.conf.eval_conf.base_dir

        target_path = os.path.normpath(os.path.join(base_dir, path))
        if not target_path.startswith(base_dir):
            return jsonify({"error": "Invalid path"}), 403

        if not os.path.exists(target_path):
            return jsonify({"error": "Path not found"}), 404

        if os.path.isfile(target_path):
            return jsonify({"error": "Path is a file, not a directory"}), 400

        items = []
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            items.append({
                "name": item,
                "path": os.path.relpath(item_path, base_dir),
                "is_dir": os.path.isdir(item_path),
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                "lines": count_lines(item_path) if os.path.isfile(item_path) else 0
            })

        return jsonify({
            "home": sqlyzr.conf.eval_conf.base_dir,
            "path": path,
            "items": items
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/files/content', methods=['GET'])
def get_file_content():
    try:
        path = request.args.get('path', '')
        sqlyzr = Sqlyzr(CONFIG_FILE)
        base_dir = sqlyzr.conf.eval_conf.base_dir

        target_path = os.path.normpath(os.path.join(base_dir, path))
        if not target_path.startswith(base_dir):
            return jsonify({"error": "Invalid path"}), 403

        if not os.path.exists(target_path):
            return jsonify({"error": "File not found"}), 404

        if not os.path.isfile(target_path):
            return jsonify({"error": "Path is a directory, not a file"}), 400

        with open(target_path, 'r') as f:
            content = f.read()

        return jsonify({
            "path": path,
            "content": content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route('/', methods=['GET'])
def serve_ui():
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui/dist'), 'index.html')


@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    vue_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui/dist')
    vue_file = os.path.join(vue_dir, path)

    if os.path.exists(vue_file) and os.path.isfile(vue_file):
        return send_from_directory(vue_dir, path)

    return send_from_directory(vue_dir, 'index.html')


@app.errorhandler(Exception)
def handle_exception(e):
    print(e)
    return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    configure_logging()
    SqlyzrLock.setup_signals()
    if platform.system() == "Linux":
        mp.set_start_method("spawn", force=True)
    port = int(os.environ.get('WEB_PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)
