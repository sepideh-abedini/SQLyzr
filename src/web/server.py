import asyncio
import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import NotFound, HTTPException

from src.app_setup import setup_app
from src.web.api.aug_api import AugAPI
from src.web.api.config_api import ConfigAPI
from src.web.api.env_api import EnvAPI
from src.web.api.files_api import FilesAPI
from src.web.api.data_api import DataAPI
from src.web.api.db_api import DBAPI
from src.web.api.models_api import ModelsAPI
from src.web.api.process_api import ProcessAPI
from src.web.api.results_api import ResultsAPI
from src.web.api.run_api import RunAPI
from src.web.api.trs_api import TrsAPI
from src.web.api.ui_api import UIServeAPI
from src.web.api.utils_api import UtilsAPI

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "gui.json"

background_tasks = {}


def register_api_routes(app, config_file):
    config_api = ConfigAPI(app, config_file)
    env_api = EnvAPI(app, config_file)
    run_api = RunAPI(app, config_file)
    results_api = ResultsAPI(app, config_file)
    files_api = FilesAPI(app, config_file)
    data_api = DataAPI(app, config_file)
    db_api = DBAPI(app, config_file)
    models_api = ModelsAPI(app, config_file)
    process_api = ProcessAPI(app, config_file)
    trs_api = TrsAPI(app, config_file)
    ui_api = UIServeAPI(app, config_file)
    utils_api = UtilsAPI(app, config_file)
    aug_api = AugAPI(app, config_file)

    config_api.register_routes()
    env_api.register_routes()
    run_api.register_routes()
    results_api.register_routes()
    files_api.register_routes()
    data_api.register_routes()
    db_api.register_routes()
    models_api.register_routes()
    process_api.register_routes()
    trs_api.register_routes()
    ui_api.register_routes()
    utils_api.register_routes()
    aug_api.register_routes()


@app.errorhandler(HTTPException)
def handle_exception(e):
    logging.error(e)
    return jsonify({"error": e.description}), e.code


register_api_routes(app, CONFIG_FILE)
# app = WsgiToAsgi(app)

if __name__ == '__main__':
    setup_app()

    port = int(os.environ.get('SQLYZR_WEB_PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)
