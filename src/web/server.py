import asyncio
import multiprocessing as mp
import os
import platform
import time

from asgiref.wsgi import WsgiToAsgi
from flask import Flask, jsonify
from flask_cors import CORS

from src.sqlyzr.sqlyzr_lock import SqlyzrLock
from src.util.log_util import configure_logging
from src.web.api.config_api import ConfigAPI
from src.web.api.files_api import FilesAPI
from src.web.api.models_api import ModelsAPI
from src.web.api.results_api import ResultsAPI
from src.web.api.run_api import RunAPI
from src.web.api.ui_api import UIServeAPI

app = Flask(__name__)
CORS(app)
asgi_app = WsgiToAsgi(app)

CONFIG_FILE = "gui.json"


def register_api_routes(app, config_file):
    config_api = ConfigAPI(app, config_file)
    run_api = RunAPI(app, config_file)
    results_api = ResultsAPI(app, config_file)
    files_api = FilesAPI(app, config_file)
    models_api = ModelsAPI(app, config_file)
    ui_api = UIServeAPI(app, config_file)

    config_api.register_routes()
    run_api.register_routes()
    results_api.register_routes()
    files_api.register_routes()
    models_api.register_routes()
    ui_api.register_routes()


async def foo():
    for i in range(10):
        time.sleep(1)
        print(i)
    return 10


@app.route('/api/bar', methods=['POST'])
async def bar():
    print("Foo started")
    task = asyncio.create_task(foo())
    task.add_done_callback(lambda t: print(f"Foo done: {t.result()}"))
    return jsonify({"msg": "salam"}), 200


@app.route('/api/trs', methods=['GET'])
def get_trs_file():
    pass


@app.errorhandler(Exception)
def handle_exception(e):
    print(e)
    return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    configure_logging()
    SqlyzrLock.setup_signals()

    register_api_routes(app, CONFIG_FILE)

    if platform.system() == "Linux":
        mp.set_start_method("spawn", force=True)

    port = int(os.environ.get('WEB_PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)
