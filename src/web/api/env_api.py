import os
import re
from flask import jsonify, request
from .base_api import BaseAPI


class EnvAPI(BaseAPI):

    def __init__(self, app, config_file):
        super().__init__(app, config_file)
        self.env_file = ".env"

    def register_routes(self):
        self.app.route('/api/env', methods=['GET'])(self.get_env_vars)
        self.app.route('/api/env', methods=['POST'])(self.update_env_vars)

    def get_env_vars(self):
        env_vars = {}

        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key] = value

        return jsonify(env_vars)

    def update_env_vars(self):
        env_vars = request.json

        existing_vars = {}
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        existing_vars[key] = value

        existing_vars.update(env_vars)

        with open(self.env_file, 'w') as f:
            for key, value in existing_vars.items():
                f.write(f"{key}={value}\n")

        for key, value in env_vars.items():
            os.environ[key] = value

        return jsonify({"message": "Environment variables updated successfully"})
