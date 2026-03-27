import logging
import os
import zipfile
import shutil
from flask import jsonify, request
from .base_api import BaseAPI
from ...configs.datasets import CUSTOM_SQLITE_DATASET
from ...sqlyzr.validate import validate_dataset


class DataAPI(BaseAPI):

    def register_routes(self):
        self.app.route('/api/data', methods=['GET'])(self.list_data_files)
        self.app.route('/api/data/content', methods=['GET'])(self.get_data_file_content)
        self.app.route('/api/data/delete_all', methods=['POST'])(self.delete_all_data_files)
        self.app.route('/api/data/delete', methods=['POST'])(self.delete_data_file)
        self.app.route('/api/data/upload', methods=['POST'])(self.upload_zip)
        self.app.route('/api/data/rename', methods=['POST'])(self.rename_item)

    def count_lines(self, filename):
        try:
            with open(filename, 'rb') as f:
                return sum(1 for _ in f)
        except:
            return 0

    def get_data_dir(self):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data')

    def list_data_files(self):
        try:
            path = request.args.get('path', '')
            base_dir = self.get_data_dir()

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
                is_file = os.path.isfile(item_path)
                items.append({
                    "name": item,
                    "path": os.path.relpath(item_path, base_dir),
                    "is_dir": not is_file,
                    "size": os.path.getsize(item_path) if is_file else 0,
                    "lines": self.count_lines(item_path) if is_file else 0
                })

            return jsonify({
                "home": "data",
                "path": path,
                "items": items
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_data_file_content(self):
        try:
            path = request.args.get('path', '')
            base_dir = self.get_data_dir()

            target_path = os.path.normpath(os.path.join(base_dir, path))
            if not target_path.startswith(base_dir):
                return jsonify({"error": "Invalid path"}), 403

            if not os.path.exists(target_path):
                return jsonify({"error": "File not found"}), 404

            if not os.path.isfile(target_path):
                return jsonify({"error": "Path is a directory, not a file"}), 400

            try:
                with open(target_path, 'r') as f:
                    content = f.read()
            except UnicodeDecodeError:
                return jsonify({
                    "path": path,
                    "content": "[Binary file content not displayed]"
                })

            return jsonify({
                "path": path,
                "content": content
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def delete_all_data_files(self):
        try:
            path = request.args.get('path', '')
            base_dir = self.get_data_dir()

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
                else:
                    shutil.rmtree(item_path)
                    deleted_count += 1

            return jsonify({
                "success": True,
                "deleted_count": deleted_count
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def delete_data_file(self):
        try:
            path = request.args.get('path', '')
            base_dir = self.get_data_dir()

            target_path = os.path.normpath(os.path.join(base_dir, path))
            if not target_path.startswith(base_dir):
                return jsonify({"error": "Invalid path"}), 403

            if not os.path.exists(target_path):
                return jsonify({"error": "Path not found"}), 404

            if os.path.isfile(target_path):
                os.remove(target_path)
                return jsonify({
                    "success": True,
                    "message": "File deleted successfully"
                })
            elif os.path.isdir(target_path):
                shutil.rmtree(target_path)
                return jsonify({
                    "success": True,
                    "message": "Directory deleted successfully"
                })
            else:
                return jsonify({"error": "Unknown file type"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    async def upload_zip(self):
        try:
            overwrite = request.args.get('overwrite', 'false').lower() == 'true'
            base_dir = self.get_data_dir()

            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400

            if os.path.exists(CUSTOM_SQLITE_DATASET.dataset_dir):
                if overwrite:
                    shutil.rmtree(CUSTOM_SQLITE_DATASET.dataset_dir)
                else:
                    return jsonify({
                        "error": f"Directory exists: {CUSTOM_SQLITE_DATASET.dataset_dir}, it should be removed before uploading new dataset"}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400

            if not file.filename.endswith('.zip'):
                return jsonify({"error": "File must be a zip archive"}), 400

            zip_name = os.path.splitext(file.filename)[0]
            temp_zip_path = os.path.join(base_dir, file.filename)
            file.save(temp_zip_path)
            target_dir = CUSTOM_SQLITE_DATASET.dataset_dir
            try:
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                os.remove(temp_zip_path)
                await validate_dataset([CUSTOM_SQLITE_DATASET])
                return jsonify({
                    "success": True,
                    "message": f"Zip file extracted to {zip_name}",
                    "path": os.path.relpath(target_dir, base_dir)
                })
            except Exception as e:
                print(f"Dataset validation failed: {e}")
                if os.path.exists(target_dir):
                    os.rmdir(target_dir)
                return jsonify({"error": "Invalid Dataset!"}), 400


        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def rename_item(self):
        try:
            data = request.get_json()
            if not data or 'path' not in data or 'new_name' not in data:
                return jsonify({"error": "Missing required parameters"}), 400

            path = data['path']
            new_name = data['new_name']

            base_dir = self.get_data_dir()

            # Validate the new name
            if not new_name or '/' in new_name or '\\' in new_name:
                return jsonify({"error": "Invalid new name"}), 400

            # Get the source path
            source_path = os.path.normpath(os.path.join(base_dir, path))
            if not source_path.startswith(base_dir):
                return jsonify({"error": "Invalid path"}), 403

            if not os.path.exists(source_path):
                return jsonify({"error": "Path not found"}), 404

            # Get the parent directory
            parent_dir = os.path.dirname(source_path)

            # Create the destination path
            dest_path = os.path.join(parent_dir, new_name)

            # Check if destination already exists
            if os.path.exists(dest_path):
                return jsonify({"error": "A file or directory with that name already exists"}), 400

            # Rename the file or directory
            os.rename(source_path, dest_path)

            return jsonify({
                "success": True,
                "message": "Item renamed successfully",
                "new_path": os.path.relpath(dest_path, base_dir)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
