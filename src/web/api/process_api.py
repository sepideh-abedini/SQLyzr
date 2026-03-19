import os
import subprocess
import sys
import threading
import time
from typing import Dict, Optional

import psutil
from dotenv import dotenv_values
from flask import jsonify

from .base_api import BaseAPI
from ...ipc.messanger import Messanger
from ...sqlyzr.sqlyzr import Sqlyzr
from loguru import logger


class ProcessAPI(BaseAPI):
    process: Optional[subprocess.Popen]

    def __init__(self, app, config_file):
        super().__init__(app, config_file)
        self.process = None

    def register_routes(self):
        self.app.route('/api/process/run', methods=['POST'])(self.run_process)
        self.app.route('/api/process/kill', methods=['POST'])(self.kill_process)
        self.app.route('/api/process/status', methods=['GET'])(self.get_process_status)

    def run_process(self):
        script_path = "src/run_gui.py"

        if not os.path.exists(script_path):
            return jsonify({"error": f"Script not found: {script_path}"}), 404
        process_id = str(hash(script_path + str(os.urandom(4))))

        try:
            env = os.environ.copy()
            print("MYSQL_HOST===============", env.get("MYSQL_HOST"))
            env.update(dotenv_values(".env"))
            env.update({'PATH': f"/opt/venv/bin:{env.get('PATH')}"})
            # with open("std.log", 'w') as std_file:
            #     process = subprocess.Popen(
            #         ['python', script_path],
            #         stdout=std_file,
            #         stderr=std_file,
            #         text=True,
            #         env=env
            #         bufsize=1
            #     )

            process = subprocess.Popen(
                [sys.executable, "-u", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            self.process = process

            def log_reader(pipe, logger):
                with pipe:
                    for line in iter(pipe.readline, ''):
                        logger.info(f"[Subprocess {self.process.pid}]: {line.strip()}")
                logger.info("Subprocess log stream closed.")

            thread = threading.Thread(target=log_reader, args=(self.process.stdout, logger))
            thread.daemon = True
            thread.start()

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
            return jsonify({"Message": f"Process not found: {print}"}), 200

        status = self._get_single_process_status(self.process)
        status['msg'] = Messanger(self.process.pid).read()
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
                status["cpu_percent"] = round(proc.cpu_percent(interval=0.1), 2)
                status["cpu_percent_max"] = 100 * psutil.cpu_count(logical=True)
                status["memory_percent"] = round(proc.memory_percent(), 2)
                status["memory_gb"] = round(proc.memory_info().rss / (1024 * 1024 * 1024), 2)
                status["create_time"] = proc.create_time()
                status["elapsed_time"] = round(time.time() - proc.create_time(), 2)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                status["running"] = False
        return status
