import logging
import os
from flask import jsonify, request
from src.sqlyzr.sqlyzr import Sqlyzr
from src.sqlyzr.pipeline_config import SQLYZR_PIPELINE_STATUS_PATH
from src.sqlyzr.sqlyzr_lock import SQLYZR_LOCK_PATH
from src.util.file_utils import read_json
from .base_api import BaseAPI

class RunAPI(BaseAPI):
    """API for run-related endpoints"""
    
    def register_routes(self):
        """Register run-related routes with the Flask application"""
        self.app.route('/api/run', methods=['POST'])(self.run_sqlyzr)
        self.app.route('/api/run/status', methods=['GET'])(self.get_run_status)
        self.app.route('/api/pipeline/status', methods=['GET'])(self.get_pipeline_status)
    
    async def run_sqlyzr(self):
        """Run the SQLyzr pipeline"""
        logging.info("Running SQlyzr")
        sqlyzr = Sqlyzr(self.config_file)
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
    
    def get_run_status(self):
        """Get the current run status"""
        is_running = os.path.exists(SQLYZR_LOCK_PATH)
        return jsonify({"is_running": is_running})
    
    def get_pipeline_status(self):
        """Get the current pipeline status"""
        if os.path.exists(SQLYZR_PIPELINE_STATUS_PATH):
            data = read_json(SQLYZR_PIPELINE_STATUS_PATH)
        else:
            data = {}
        return jsonify(data)