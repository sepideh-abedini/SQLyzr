import os
from os.path import isdir

import pandas as pd
from flask import jsonify, send_file
from src.sqlyzr.sqlyzr import Sqlyzr
from .base_api import BaseAPI

COLUMN_NAMES = {
    "ea_mean": "Mean Execution Accuracy",
    "model": "System",
    "tmp": "Temperature",
    "cat": "Category",
    "sub": "Subcategory",
    "em_mean": "Mean Exact Match",
    "rea_mean": "Mean Relaxed Execution Accuracy",
    "et_mean": "Mean Execution Time",
    "get_mean": "Mean Gold Execution Time",
    "cc": "Complexity Consistency",
    "etc": "Execution Time Consistency",
    "em_ci": "Exact Match Confidence Interval",
    "ea_ci": "Execution Accuracy Confidence Interval",
    "rea_ci": "Relaxed Execution Accuracy Confidence Interval",
    "et_ci": "Execution Time Confidence Interval",
    "get_ci": "Gold Execution Time Confidence Interval",
    "count_sum": "Count"
}

DROP_COLS = ['count_mean', 'count_ci']


class ResultsAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/results', methods=['GET'])(self.get_results)
        self.app.route('/api/charts', methods=['GET'])(self.get_charts)
        self.app.route('/api/charts/<hue>/<chart_name>', methods=['GET'])(self.get_chart)
        self.app.route('/api/logs', methods=['GET'])(self.get_logs)
        self.app.route('/api/logs', methods=['DELETE'])(self.clear_logs)

    def get_results(self):
        try:
            sqlyzr = Sqlyzr(self.config_file)
            results_path = sqlyzr.conf.eval_conf.get_scores_path()

            if os.path.exists(results_path):
                df = pd.read_csv(results_path)
                df = df.rename(columns=COLUMN_NAMES)
                df = df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")])
                df = df.drop(columns=[col for col in df.columns if col.endswith("_sum")])
                df = df.drop(columns=[col for col in df.columns if col in DROP_COLS])
                data = {
                    "headers": df.columns.tolist(),
                    "rows": df.values.tolist()
                }
                return jsonify({
                    "data": data
                })
            else:
                return jsonify({
                    "message": "No results file found"
                }), 200
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 500

    def get_charts(self):
        try:
            sqlyzr = Sqlyzr(self.config_file)
            avail_charts = dict()
            if os.path.exists(sqlyzr.conf.eval_conf.charts_dir):
                hues = [os.path.basename(f) for f in os.listdir(sqlyzr.conf.eval_conf.charts_dir)]
                for hue in hues:
                    hue_dir = os.path.join(sqlyzr.conf.eval_conf.charts_dir, hue)
                    if os.path.exists(hue_dir) and os.path.isdir(hue_dir):
                        chart_names = [os.path.basename(f) for f in os.listdir(hue_dir)]
                        for chart_name in chart_names:
                            avail_charts.setdefault(hue, []).append(chart_name)
                            # files.append(str(os.path.join(hue, chart_name)))
            return jsonify({
                "avail_charts": avail_charts,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_chart(self, hue, chart_name):
        try:
            sqlyzr = Sqlyzr(self.config_file)
            full_path = os.path.join(sqlyzr.conf.eval_conf.charts_dir, hue, chart_name)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                full_path = "../../" + full_path
                return send_file(full_path)
            else:
                return jsonify({"error": f"Chart '{chart_name}' not found"}), 404
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 500

    def get_logs(self):
        try:
            log_file_path = "std.log"
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as f:
                    logs = f.read()
                return jsonify({"logs": logs})
            else:
                return jsonify({"error": "Log file not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def clear_logs(self):
        log_file_path = "std.log"
        with open(log_file_path, 'w') as f:
            f.truncate()
        return jsonify({"message": "Logs cleared"})
