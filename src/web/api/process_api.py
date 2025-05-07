import os
import subprocess
import psutil
import time
from typing import Dict, Optional
from dotenv import dotenv_values

from flask import jsonify, request
from .base_api import BaseAPI


class ProcessAPI(BaseAPI):
    """API for managing external processes"""
    process: Optional[subprocess.Popen]

    def __init__(self, app, config_file):
        super().__init__(app, config_file)
        self.process = None

    def register_routes(self):
        """Register routes with the Flask application"""
        self.app.route('/api/process/run', methods=['POST'])(self.run_process)
        self.app.route('/api/process/kill', methods=['POST'])(self.kill_process)
        self.app.route('/api/process/status', methods=['GET'])(self.get_process_status)

    def run_process(self):
        script_path = "temp.py"
        if not os.path.exists(script_path):
            return jsonify({"error": f"Script not found: {script_path}"}), 404

        process_id = str(hash(script_path + str(os.urandom(4))))

        try:

            env = os.environ.copy()
            env.update(dotenv_values(".env"))
            process = subprocess.Popen(
                ['python', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            self.process = process
            return jsonify({
                "message": "Process started",
                "process_id": process_id,
                "pid": process.pid
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def kill_process(self):
        if not self.process:
            return jsonify({"error": "Process ID is required"}), 400

        try:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.process = None
            return jsonify({"message": "Process killed"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_process_status(self):
        if not self.process:
            return jsonify({"error": f"Process not found: {print}"}), 404

        status = self._get_single_process_status(self.process)
        return jsonify(status)

    def _get_single_process_status(self, process: subprocess.Popen) -> Dict:
        status = {
            "pid": process.pid,
            "running": process.poll() is None,
            "return_code": process.returncode
        }

        if status["running"]:
            try:
                proc = psutil.Process(process.pid)
                status["cpu_percent"] = proc.cpu_percent(interval=0.1)
                status["memory_mb"] = proc.memory_info().rss / (1024 * 1024)  # Convert to MB
                status["create_time"] = proc.create_time()
                status["elapsed_time"] = time.time() - proc.create_time()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                status["running"] = False
        return status
