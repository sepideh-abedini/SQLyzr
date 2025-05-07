import os
from flask import jsonify, request
from src.sqlyzr.sqlyzr import Sqlyzr
from .base_api import BaseAPI


class FilesAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/files', methods=['GET'])(self.list_files)
        self.app.route('/api/files/content', methods=['GET'])(self.get_file_content)
        self.app.route('/api/files/delete_all', methods=['POST'])(self.delete_all_files)

    def count_lines(self, filename):
        with open(filename, 'rb') as f:
            return sum(1 for _ in f)

    def list_files(self):
        try:
            path = request.args.get('path', '')
            sqlyzr = Sqlyzr(self.config_file)
            base_dir = sqlyzr.conf.eval_conf.base_dir

            target_path = os.path.normpath(os.path.join(base_dir, path))
            if not target_path.startswith(base_dir):
                return jsonify({"error": "Invalid path"}), 403

            if not os.path.exists(target_path):
                return jsonify({"error": "Path not found"}), 404

            if os.path.isfile(target_path):
                return jsonify({"error": "Path is a file, not a directory"}), 400

            items = []
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                items.append({
                    "name": item,
                    "path": os.path.relpath(item_path, base_dir),
                    "is_dir": os.path.isdir(item_path),
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                    "lines": self.count_lines(item_path) if os.path.isfile(item_path) else 0
                })

            return jsonify({
                "home": sqlyzr.conf.eval_conf.base_dir,
                "path": path,
                "items": items
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_file_content(self):
        try:
            path = request.args.get('path', '')
            sqlyzr = Sqlyzr(self.config_file)
            base_dir = sqlyzr.conf.eval_conf.base_dir

            target_path = os.path.normpath(os.path.join(base_dir, path))
            if not target_path.startswith(base_dir):
                return jsonify({"error": "Invalid path"}), 403

            if not os.path.exists(target_path):
                return jsonify({"error": "File not found"}), 404

            if not os.path.isfile(target_path):
                return jsonify({"error": "Path is a directory, not a file"}), 400

            with open(target_path, 'r') as f:
                content = f.read()

            return jsonify({
                "path": path,
                "content": content
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def delete_all_files(self):
        try:
            path = request.args.get('path', '')
            sqlyzr = Sqlyzr(self.config_file)
            base_dir = sqlyzr.conf.eval_conf.base_dir

            target_path = os.path.normpath(os.path.join(base_dir, path))
            if not target_path.startswith(base_dir):
                return jsonify({"error": "Invalid path"}), 403

            if not os.path.exists(target_path):
                return jsonify({"error": "Path not found"}), 404

            if os.path.isfile(target_path):
                return jsonify({"error": "Path is a file, not a directory"}), 400

            deleted_count = 0
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    deleted_count += 1

            return jsonify({
                "success": True,
                "deleted_count": deleted_count
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
