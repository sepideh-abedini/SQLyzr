import os
from flask import send_from_directory
from .base_api import BaseAPI


class UIServeAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/', methods=['GET'])(self.serve_ui)
        self.app.route('/api/health', methods=['GET'])(self.health_check)
        self.app.route('/<path:path>', methods=['GET'])(self.serve_static)

    def serve_ui(self):
        return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../ui/dist'), 'index.html')

    def serve_static(self, path):
        vue_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../ui/dist')
        vue_file = os.path.join(vue_dir, path)

        if os.path.exists(vue_file) and os.path.isfile(vue_file):
            return send_from_directory(vue_dir, path)

        return send_from_directory(vue_dir, 'index.html')

    def health_check(self):
        return {"status": "ok"}, 200
