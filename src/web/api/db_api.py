import os
from flask import jsonify, request
from .base_api import BaseAPI
from ...configs.datasets import SPIDER_ALL
from ...rel.db_facade import DatabaseFacade
from ...rel.db_factory import DatabaseFactory
from ...scalar.tmp import scale_db
from ...scalar.utils.export_ddls import revert_backup
from ...scalar.utils.table_meta import get_tables, exec_sql
from ...util.file_utils import read_json


class DBAPI(BaseAPI):
    """API for database operations"""

    def register_routes(self):
        self.app.route('/api/db/list', methods=['GET'])(self.list_databases)
        self.app.route('/api/db/table_rows', methods=['GET'])(self.get_table_rows)
        self.app.route('/api/db/scale', methods=['POST'])(self.scale_db)
        self.app.route('/api/db/revert', methods=['GET'])(self.revert)

    def list_databases(self):
        conf = SPIDER_ALL
        test_data = read_json(conf.get_test_path())
        db_ids = list(set(map(lambda x: x['db_id'], test_data)))
        try:
            return jsonify({
                "db_ids": db_ids
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_table_rows(self):
        """Get row counts for all tables in a database"""
        conf = SPIDER_ALL
        db_facade = DatabaseFactory.get_instance(conf)
        try:
            db_id = request.args.get('db_id')
            if not db_id:
                return jsonify({"error": "Missing db_id parameter"}), 400

            tables = db_facade.get_tables(db_id)
            table_rows = []

            for table in sorted(tables):
                try:
                    result = db_facade.exec_query_sync(db_id, f"SELECT COUNT(*) FROM {table}")
                    row_count = result[0][0]
                    table_rows.append({
                        "table": table,
                        "rows": row_count
                    })
                except Exception as e:
                    table_rows.append({
                        "table": table,
                        "error": str(e)
                    })

            return jsonify({
                "db_id": db_id,
                "tables": table_rows
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def scale_db(self):
        """Scale database by the specified factor"""
        try:
            db_id = request.args.get('db_id')
            if not db_id:
                return jsonify({"error": "Missing db_id parameter"}), 400

            scale = request.args.get('scale')
            if not scale:
                return jsonify({"error": "Missing scale parameter"}), 400

            try:
                scale_factor = int(scale)
                if scale_factor < 1 or scale_factor > 100:
                    return jsonify({"error": "Scale factor must be between 1 and 100"}), 400
            except ValueError:
                return jsonify({"error": "Scale factor must be an integer"}), 400

            scale_db(db_id, scale_factor)
            return jsonify({"message": "Database scaled successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def revert(self):
        """Revert database to its original state"""
        try:
            db_id = request.args.get('db_id')
            if not db_id:
                return jsonify({"error": "Missing db_id parameter"}), 400

            revert_backup(SPIDER_ALL.get_db_path(), db_id)
            return jsonify({"message": "Database reverted successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
