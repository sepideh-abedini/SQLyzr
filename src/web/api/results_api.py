import os
import pandas as pd
from flask import jsonify, send_file
from src.sqlyzr.sqlyzr import Sqlyzr
from .base_api import BaseAPI

class ResultsAPI(BaseAPI):
    """API for results-related endpoints"""
    
    def register_routes(self):
        """Register results-related routes with the Flask application"""
        self.app.route('/api/results', methods=['GET'])(self.get_results)
        self.app.route('/api/charts', methods=['GET'])(self.get_charts)
        self.app.route('/api/charts/<chart_name>', methods=['GET'])(self.get_chart)
        self.app.route('/api/log', methods=['GET'])(self.get_logs)
    
    def get_results(self):
        """Get the results of the SQLyzr pipeline"""
        try:
            sqlyzr = Sqlyzr(self.config_file)
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
    
    def get_charts(self):
        """Get the list of available charts"""
        try:
            sqlyzr = Sqlyzr(self.config_file)
            files = [os.path.basename(f) for f in os.listdir(sqlyzr.conf.eval_conf.charts_dir)]
            return jsonify({
                "charts": files,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_chart(self, chart_name):
        """Get a specific chart"""
        try:
            sqlyzr = Sqlyzr(self.config_file)
            full_path = os.path.join(sqlyzr.conf.eval_conf.charts_dir, chart_name)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                full_path = "../../" + full_path
                return send_file(full_path)
            else:
                return jsonify({"error": f"Chart '{chart_name}' not found"}), 404
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 500
    
    def get_logs(self):
        """Get the logs of the SQLyzr pipeline"""
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