import asyncio
import logging
import os
from typing import Optional

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend
from flask import jsonify

from src.sqlyzr.pipeline_config import SQLYZR_PIPELINE_STATUS_PATH
from src.sqlyzr.sqlyzr_lock import SQLYZR_LOCK_PATH
from src.util.file_utils import read_json
from .base_api import BaseAPI

redis_broker = RedisBroker()
result_backend = RedisBackend()
redis_broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(redis_broker)


@dramatiq.actor
async def bar(self):
    try:
        print("STARTING SQLYZR")
        await asyncio.sleep(20)
        print("FINISHED SQLYZR")
    except asyncio.CancelledError:
        print("CANCELLED SQLYZR")


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
        self.msg = bar.send()
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
