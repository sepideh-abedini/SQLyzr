import asyncio
import os

import dramatiq
from flask import jsonify

from src.sqlyzr.pipeline_config import SQLYZR_PIPELINE_STATUS_PATH
from src.sqlyzr.sqlyzr_lock import SQLYZR_LOCK_PATH
from src.util.file_utils import read_json
from .base_api import BaseAPI
from src.run_gui import run_gui


class RunAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/run', methods=['POST'])(self.run_sqlyzr)
        self.app.route('/api/kill', methods=['POST'])(self.kill_sqlyzr)
        self.app.route('/api/run/status', methods=['GET'])(self.get_run_status)
        self.app.route('/api/pipeline/status', methods=['GET'])(self.get_pipeline_status)
        self.msg = None

    def kill_sqlyzr(self, task=None):
        pass

    def run_sqlyzr(self):
        run_gui()
        return jsonify({"message": "Started"})

    def get_run_status(self):
        is_running = os.path.exists(SQLYZR_LOCK_PATH)
        return jsonify({"is_running": is_running})

    def get_pipeline_status(self):
        if os.path.exists(SQLYZR_PIPELINE_STATUS_PATH):
            data = read_json(SQLYZR_PIPELINE_STATUS_PATH)
        else:
            data = {}
        return jsonify(data)
