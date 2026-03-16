import os
import subprocess
import sys
import threading

from flask import jsonify, request, send_file
from loguru import logger

from .base_api import BaseAPI
from ...configs.config_loader import load_config
from ...sqlyzr.augment_data import DatasetAugmentor
from ...sqlyzr.sqlyzr import Sqlyzr
from ...util.file_utils import read_json, write_json

AUG_CONF = "tests/aug.json"


class AugAPI(BaseAPI):
    def __init__(self, app, config_file):
        super().__init__(app, config_file)
        self.process = None

    def register_routes(self):
        self.app.route('/api/aug/stats', methods=['GET'])(self.get_ds_stats)
        self.app.route('/api/aug/start/<script>', methods=['POST'])(self.start_eval)
        self.app.route('/api/aug/config', methods=['GET'])(self.get_aug_config)
        self.app.route('/api/aug/save', methods=['POST'])(self.update_aug_config)
        self.app.route('/api/aug/status', methods=['GET'])(self.get_eval_status)
        self.app.route('/api/aug/plot/<name>', methods=['GET'])(self.get_plot)
        self.app.route('/api/aug/clear', methods=['POST'])(self.clear)

    def get_ds_stats(self):
        dataset_size = 0
        conf = load_config(AUG_CONF)
        for ds in conf.eval_conf.dataset_configs:
            data = read_json(ds.get_test_path())
            dataset_size += len(data)
        try:
            return jsonify({
                "dataset_size": dataset_size
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    async def clear(self):
        conf = load_config(AUG_CONF)
        conf.clear()
        return jsonify({
            "message": "Clear done!"
        }), 200

    def start_eval(self, script):
        logger.info("Starting script")
        try:
            if self.process and self.process.poll() is None:
                return jsonify({"error": "A process is already running", "pid": self.process.pid}), 400

            script_path = f"src/sqlyzr/run_{script}_cli.py"
            if not os.path.exists(script_path):
                return jsonify({"error": f"Script file not found at {script_path}"}), 404

            self.process = subprocess.Popen(
                [sys.executable, "-u", script_path, "--config", AUG_CONF],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                text=True,
                bufsize=1  # Line buffered
            )

            def log_reader(pipe, logger):
                with pipe:
                    for line in iter(pipe.readline, ''):
                        logger.info(f"[Subprocess {self.process.pid}]: {line.strip()}")
                logger.info("Subprocess log stream closed.")

            # Start the thread to consume the logs
            thread = threading.Thread(target=log_reader, args=(self.process.stdout, logger))
            thread.daemon = True  # Thread dies if the main process dies
            thread.start()

            return jsonify({
                "message": "Script started successfully",
                "pid": self.process.pid
            }), 202
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_eval_status(self):
        if self.process is None:
            return jsonify({"status": "no_process_found"}), 404

        exit_code = self.process.poll()

        if exit_code is None:
            return jsonify({
                "status": "running",
                "pid": self.process.pid
            })
        else:
            return jsonify({
                "status": "completed",
                "exit_code": exit_code,
                "pid": self.process.pid
            })

    def get_plot(self, name):
        conf = load_config(AUG_CONF)
        logger.info(conf.get_aug_out("spider"))
        chart_file = f"{name}.png"
        plot_path = os.path.join(conf.eval_conf.charts_dir, chart_file)
        plot_path = os.path.normpath(plot_path)
        if os.path.exists(plot_path):
            plot_path = "../../" + plot_path
            return send_file(plot_path, mimetype='image/png')
        else:
            return jsonify({"error": f"Plot file not found at {plot_path}"}), 404

    def update_aug_config(self):
        old_config = read_json(AUG_CONF)
        config = request.json
        logger.info(f"New config: {config}")
        write_json(AUG_CONF, config)
        try:
            sqlyzr = Sqlyzr(AUG_CONF)
        except Exception as e:
            print(e)
            write_json(AUG_CONF, old_config)
            return str(e), 400
        return jsonify({"message": "Configuration updated successfully"})

    def get_aug_config(self):
        data = read_json(AUG_CONF)
        return jsonify(data)
